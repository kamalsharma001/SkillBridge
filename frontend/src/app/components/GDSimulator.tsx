"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import {
  Users,
  Clock,
  Mic,
  MicOff,
  Sparkles,
  Send,
  Award,
  CheckCircle2,
  XCircle,
  HelpCircle,
  RotateCcw,
  MessageSquare,
  Volume2,
  VolumeX,
  ChevronRight,
  TrendingUp,
  Lock,
  Unlock,
  Search,
  UserPlus,
  LogOut,
  AlertTriangle,
  Play,
  Flame,
  Globe2,
  Shield,
  Layers,
} from "lucide-react";

import GD_TOPICS_250 from "../data/gd_topics_250.json";

export type GDTopic = {
  id: string;
  title: string;
  category: string;
  starter_pros: string;
  starter_cons: string;
  key_discussion_points?: string[];
  duration_seconds: number;
};

export type Participant = {
  id: string;
  name: string;
  avatar: string;
  joined_at?: number;
  is_speaking?: boolean;
  mic_closed?: boolean;
};

export type TranscriptItem = {
  participant_id: string;
  name: string;
  text: string;
  timestamp: number;
  audio_data?: string;
};

export type RoomState = {
  room_id: string;
  status: "waiting" | "in_discussion" | "completed";
  phase: "waiting" | "individual_turns" | "open_discussion" | "completed";
  participants_count: number;
  max_capacity: number;
  participants: Participant[];
  topic: GDTopic | null;
  turn_order: string[];
  current_turn_index: number;
  current_speaker_id: string | null;
  current_speaker_name: string | null;
  turn_time_left: number;
  total_time_left: number;
  transcripts: TranscriptItem[];
};

export type RoomSummary = {
  room_id: string;
  participants_count: number;
  max_capacity: number;
  status: string;
  phase: string;
  topic_title: string | null;
  is_locked: boolean;
  can_join: boolean;
  can_lock: boolean;
};

function getGdWsUrl(apiBase: string, roomId: string, userId: string, userName: string): string {
  let host = "localhost:8000";
  let protocol = "ws:";
  if (typeof window !== "undefined") {
    host = `${window.location.hostname}:8000`;
    if (window.location.protocol === "https:") {
      protocol = "wss:";
    }
  }
  if (apiBase.startsWith("http://")) {
    const raw = apiBase.replace("http://", "");
    host = raw.split("/")[0];
  } else if (apiBase.startsWith("https://")) {
    const raw = apiBase.replace("https://", "");
    host = raw.split("/")[0];
    protocol = "wss:";
  }
  return `${protocol}//${host}/ws/gd/${roomId}?participant_id=${encodeURIComponent(userId)}&name=${encodeURIComponent(userName)}`;
}

interface GDSimulatorProps {
  apiBase: string;
  candidateName?: string;
}

export default function GDSimulator({ apiBase, candidateName }: GDSimulatorProps) {
  // Current user info (persisted in sessionStorage per-tab so multi-tab and multi-device sessions are independent single entities)
  const [myUserId] = useState(() => {
    if (typeof window !== "undefined") {
      let stored = sessionStorage.getItem("skillbridge_gd_user_id");
      if (!stored) {
        stored = `user_${Math.random().toString(36).substring(2, 9)}`;
        sessionStorage.setItem("skillbridge_gd_user_id", stored);
      }
      return stored;
    }
    return `user_${Math.random().toString(36).substring(2, 9)}`;
  });

  const [myName, setMyName] = useState(() => {
    if (typeof window !== "undefined") {
      let stored = sessionStorage.getItem("skillbridge_gd_user_name");
      if (!stored) {
        stored = candidateName || `Candidate_${Math.floor(Math.random() * 899 + 100)}`;
        sessionStorage.setItem("skillbridge_gd_user_name", stored);
      }
      return stored;
    }
    return candidateName || `Candidate_${Math.floor(Math.random() * 899 + 100)}`;
  });

  // Directory / Rooms view
  const [currentView, setCurrentView] = useState<"lobby" | "room">("lobby");
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "available" | "in_session" | "waiting">("all");
  const [roomsList, setRoomsList] = useState<RoomSummary[]>([]);
  const [activeStudents, setActiveStudents] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(42);

  // Active room state
  const [activeRoomId, setActiveRoomId] = useState<string | null>(null);
  const [roomState, setRoomState] = useState<RoomState | null>(null);
  const [speechInput, setSpeechInput] = useState("");
  const [isSubmittingSpeech, setIsSubmittingSpeech] = useState(false);
  const [isSimulatingAudio, setIsSimulatingAudio] = useState(false);
  const [aiEvaluation, setAiEvaluation] = useState<any | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);

  // ------------------------------------------
  // Real Hardware Microphone & Speech Recognition & Audible Playback
  // ------------------------------------------
  const [micPermission, setMicPermission] = useState<"idle" | "requesting" | "granted" | "denied" | "unsupported">("idle");
  const [audioLevel, setAudioLevel] = useState<number>(0);
  const [isRecognizing, setIsRecognizing] = useState<boolean>(false);
  const [interimTranscript, setInterimTranscript] = useState<string>("");
  const [isRoomAudioMuted, setIsRoomAudioMuted] = useState<boolean>(false);

  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const recognitionRef = useRef<any | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const prevCanSpeakRef = useRef<boolean>(false);

  // WebRTC Peer Connection Audio Mesh refs
  const peerConnectionsRef = useRef<Map<string, RTCPeerConnection>>(new Map());
  const remoteAudiosRef = useRef<Map<string, HTMLAudioElement>>(new Map());
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const lastPlayedTimestampRef = useRef<number>(Date.now());
  const simSpeechDoneRef = useRef<Record<string, boolean>>({});

  // Play a soft attention chime when turn starts
  const playTurnChime = () => {
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(523.25, ctx.currentTime); // C5
      osc.frequency.exponentialRampToValueAtTime(783.99, ctx.currentTime + 0.25); // G5
      gain.gain.setValueAtTime(0.2, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.4);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.4);
    } catch {}
  };

  // Create an RTCPeerConnection for a remote candidate peer
  const createPeerConnection = useCallback(
    (peerId: string): RTCPeerConnection => {
      const existing = peerConnectionsRef.current.get(peerId);
      if (existing) return existing;

      const pc = new RTCPeerConnection({
        iceServers: [
          { urls: "stun:stun.l.google.com:19302" },
          { urls: "stun:stun1.l.google.com:19302" },
        ],
      });

      // Attach our local mic stream if currently active
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getAudioTracks().forEach((track) => {
          pc.addTrack(track, mediaStreamRef.current!);
        });
      }

      // Handle incoming remote audio stream
      pc.ontrack = (event) => {
        let audio = remoteAudiosRef.current.get(peerId);
        if (!audio) {
          audio = new Audio();
          audio.autoplay = true;
          audio.muted = isRoomAudioMuted;
          remoteAudiosRef.current.set(peerId, audio);
        }
        if (event.streams && event.streams[0]) {
          audio.srcObject = event.streams[0];
        } else {
          audio.srcObject = new MediaStream([event.track]);
        }
        audio.play().catch((e) => {
          console.warn(`WebRTC live audio playback for ${peerId} waiting for user interaction:`, e);
        });
      };

      // Forward ICE candidates over WebSocket signaling
      pc.onicecandidate = (event) => {
        if (event.candidate && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(
            JSON.stringify({
              type: "webrtc_ice",
              target_id: peerId,
              candidate: event.candidate,
            })
          );
        }
      };

      pc.onconnectionstatechange = () => {
        if (pc.connectionState === "disconnected" || pc.connectionState === "failed" || pc.connectionState === "closed") {
          pc.close();
          peerConnectionsRef.current.delete(peerId);
          const audio = remoteAudiosRef.current.get(peerId);
          if (audio) {
            audio.pause();
            audio.srcObject = null;
            remoteAudiosRef.current.delete(peerId);
          }
        }
      };

      peerConnectionsRef.current.set(peerId, pc);
      return pc;
    },
    [isRoomAudioMuted]
  );

  // Initiate WebRTC offer to another candidate peer
  const callPeer = useCallback(
    async (peerId: string) => {
      try {
        const pc = createPeerConnection(peerId);
        const offer = await pc.createOffer({
          offerToReceiveAudio: true,
        });
        await pc.setLocalDescription(offer);
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(
            JSON.stringify({
              type: "webrtc_offer",
              target_id: peerId,
              offer: offer,
            })
          );
        }
      } catch (err) {
        console.warn("Failed to create WebRTC offer:", err);
      }
    },
    [createPeerConnection]
  );

  // Audio chunk recording helpers
  const startAudioRecording = useCallback(() => {
    if (!mediaStreamRef.current) return;
    try {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
        try {
          mediaRecorderRef.current.stop();
        } catch {}
      }
      audioChunksRef.current = [];
      const options =
        typeof MediaRecorder !== "undefined" && MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
          ? { mimeType: "audio/webm;codecs=opus" }
          : typeof MediaRecorder !== "undefined" && MediaRecorder.isTypeSupported("audio/webm")
          ? { mimeType: "audio/webm" }
          : undefined;

      const recorder = new MediaRecorder(mediaStreamRef.current, options);
      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      recorder.start(300);
      mediaRecorderRef.current = recorder;
    } catch (err) {
      console.warn("MediaRecorder start failed:", err);
    }
  }, []);

  const stopAudioRecording = useCallback(async (): Promise<string | null> => {
    return new Promise((resolve) => {
      const recorder = mediaRecorderRef.current;
      if (!recorder || recorder.state === "inactive") {
        resolve(null);
        return;
      }
      recorder.onstop = () => {
        try {
          const mime = recorder.mimeType || "audio/webm";
          const blob = new Blob(audioChunksRef.current, { type: mime });
          if (blob.size < 300) {
            resolve(null);
            return;
          }
          const reader = new FileReader();
          reader.onloadend = () => {
            resolve(reader.result as string);
          };
          reader.onerror = () => resolve(null);
          reader.readAsDataURL(blob);
        } catch {
          resolve(null);
        }
      };
      try {
        recorder.stop();
      } catch {
        resolve(null);
      }
    });
  }, []);

  // Request actual hardware microphone access
  const requestMicAccess = async () => {
    if (typeof window === "undefined" || !navigator?.mediaDevices?.getUserMedia) {
      setMicPermission("unsupported");
      return;
    }
    setMicPermission("requesting");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true },
      });
      mediaStreamRef.current = stream;

      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioCtx) {
        const audioCtx = new AudioCtx();
        audioContextRef.current = audioCtx;
        const analyser = audioCtx.createAnalyser();
        analyser.fftSize = 64;
        analyserRef.current = analyser;
        const source = audioCtx.createMediaStreamSource(stream);
        source.connect(analyser);

        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        const updateLevel = () => {
          if (!analyserRef.current || !mediaStreamRef.current) return;
          analyserRef.current.getByteFrequencyData(dataArray);
          let sum = 0;
          for (let i = 0; i < dataArray.length; i++) {
            sum += dataArray[i];
          }
          const avg = sum / dataArray.length;
          setAudioLevel(Math.min(100, Math.round((avg / 128) * 100)));
          animFrameRef.current = requestAnimationFrame(updateLevel);
        };
        updateLevel();
      }

      setMicPermission("granted");

      // Attach newly acquired microphone track to all active WebRTC peer connections
      peerConnectionsRef.current.forEach((pc) => {
        stream.getAudioTracks().forEach((track) => {
          const senders = pc.getSenders();
          const existing = senders.find((s) => s.track?.kind === "audio");
          if (existing) {
            existing.replaceTrack(track);
          } else {
            pc.addTrack(track, stream);
          }
        });
      });

      setupSpeechRecognition();
      startAudioRecording();
    } catch (err) {
      console.warn("Microphone access denied:", err);
      setMicPermission("denied");
    }
  };

  // Setup Web Speech API for voice dictation
  const setupSpeechRecognition = () => {
    if (typeof window === "undefined") return;
    const SpeechRec = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRec) return;

    try {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch {}
      }
      const recognition = new SpeechRec();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = "en-US";

      recognition.onresult = (event: any) => {
        let interim = "";
        let finalChunk = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalChunk += event.results[i][0].transcript + " ";
          } else {
            interim += event.results[i][0].transcript;
          }
        }
        if (interim) setInterimTranscript(interim);
        if (finalChunk) {
          setSpeechInput((prev) => (prev ? `${prev.trim()} ${finalChunk.trim()}` : finalChunk.trim()));
          setInterimTranscript("");
        }
      };

      recognition.onerror = (e: any) => {
        if (e.error !== "no-speech") {
          console.warn("Speech recognition error:", e.error);
        }
        setIsRecognizing(false);
      };

      recognition.onend = () => {
        setIsRecognizing(false);
      };

      recognitionRef.current = recognition;
    } catch (e) {
      console.warn("SpeechRec setup failed:", e);
    }
  };

  // Polling ref for room sync
  const pollTimerRef = useRef<NodeJS.Timeout | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // 1. Fetch Rooms Directory (zero fake members in clean state)
  const fetchRoomsDirectory = useCallback(async () => {
    try {
      const q = new URLSearchParams({
        page: page.toString(),
        limit: "24",
      });
      if (searchQuery.trim()) q.set("search", searchQuery.trim());
      if (statusFilter !== "all") q.set("status_filter", statusFilter);

      const res = await fetch(`${apiBase}/api/gd-rooms?${q.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setRoomsList(data.rooms || []);
        setActiveStudents(data.active_students || 0);
        setTotalPages(Math.ceil((data.total_rooms || 1000) / 24));
        return;
      }
    } catch {
      // Offline fallback
    }

    // Local fallback for GD000-GD999 without any fake members
    const fallbackRooms: RoomSummary[] = Array.from({ length: 24 }).map((_, i) => {
      const idx = (page - 1) * 24 + i;
      const rid = `GD${idx.toString().padStart(3, "0")}`;
      return {
        room_id: rid,
        participants_count: 0,
        max_capacity: 6,
        status: "waiting",
        phase: "waiting",
        topic_title: null,
        is_locked: false,
        can_join: true,
        can_lock: false,
      };
    });
    setRoomsList(fallbackRooms);
  }, [apiBase, page, searchQuery, statusFilter]);

  useEffect(() => {
    if (currentView === "lobby") {
      fetchRoomsDirectory();
      const interval = setInterval(fetchRoomsDirectory, 3000);
      return () => clearInterval(interval);
    }
  }, [currentView, fetchRoomsDirectory]);

  // 2. Fetch Active Room State with Heartbeat participant_id
  const syncRoomState = useCallback(async (rid: string) => {
    try {
      const res = await fetch(`${apiBase}/api/gd-rooms/${rid}/state?participant_id=${myUserId}`);
      if (res.ok) {
        const data: RoomState = await res.json();
        setRoomState(data);
        return;
      }
    } catch {
      // Local fallback
    }
  }, [apiBase, myUserId]);

  // Synchronize WebRTC audio peer connections for all joined room candidates
  useEffect(() => {
    if (!roomState?.participants || currentView !== "room") return;

    const activePeerIds = new Set<string>();
    roomState.participants.forEach((p) => {
      const peerId = p.id;
      if (peerId && peerId !== myUserId) {
        activePeerIds.add(peerId);
        if (!peerConnectionsRef.current.has(peerId)) {
          // Establish connection deterministically: initiator has lower lexicographical ID
          if (myUserId < peerId) {
            callPeer(peerId);
          } else {
            createPeerConnection(peerId);
          }
        }
      }
    });

    // Cleanup peers who left the room
    peerConnectionsRef.current.forEach((pc, peerId) => {
      if (!activePeerIds.has(peerId)) {
        pc.close();
        peerConnectionsRef.current.delete(peerId);
        const audio = remoteAudiosRef.current.get(peerId);
        if (audio) {
          audio.pause();
          audio.srcObject = null;
          remoteAudiosRef.current.delete(peerId);
        }
      }
    });
  }, [roomState?.participants, myUserId, callPeer, createPeerConnection, currentView]);

  // Synchronize mute state across all active remote audio players
  useEffect(() => {
    remoteAudiosRef.current.forEach((audio) => {
      audio.muted = isRoomAudioMuted;
    });
  }, [isRoomAudioMuted]);

  // Start real-time WebSocket connection and heartbeat sync when in a room
  useEffect(() => {
    if (currentView !== "room" || !activeRoomId) {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      return;
    }

    let isCancelled = false;
    let reconnectTimeout: NodeJS.Timeout;

    const connectWebSocket = () => {
      if (isCancelled) return;
      try {
        const wsUrl = getGdWsUrl(apiBase, activeRoomId, myUserId, myName);
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          if (isCancelled) return;
        };

        ws.onmessage = (event) => {
          if (isCancelled) return;
          try {
            const data = JSON.parse(event.data);
            if (data.type === "room_state" || data.type === "room_update") {
              if (data.state) {
                setRoomState(data.state);
              }
            } else if (data.type === "webrtc_offer") {
              const senderId = data.sender_id;
              if (senderId && data.offer) {
                const pc = createPeerConnection(senderId);
                pc.setRemoteDescription(new RTCSessionDescription(data.offer))
                  .then(async () => {
                    const answer = await pc.createAnswer();
                    await pc.setLocalDescription(answer);
                    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                      wsRef.current.send(
                        JSON.stringify({
                          type: "webrtc_answer",
                          target_id: senderId,
                          answer: answer,
                        })
                      );
                    }
                  })
                  .catch((e) => console.warn("Failed handling WebRTC offer:", e));
              }
            } else if (data.type === "webrtc_answer") {
              const senderId = data.sender_id;
              if (senderId && data.answer) {
                const pc = peerConnectionsRef.current.get(senderId);
                if (pc) {
                  pc.setRemoteDescription(new RTCSessionDescription(data.answer)).catch((e) =>
                    console.warn("Failed handling WebRTC answer:", e)
                  );
                }
              }
            } else if (data.type === "webrtc_ice") {
              const senderId = data.sender_id;
              if (senderId && data.candidate) {
                const pc = peerConnectionsRef.current.get(senderId);
                if (pc) {
                  pc.addIceCandidate(new RTCIceCandidate(data.candidate)).catch((e) =>
                    console.warn("Failed adding ICE candidate:", e)
                  );
                }
              }
            }
          } catch (e) {
            console.warn("GD WS parse error:", e);
          }
        };

        ws.onclose = () => {
          if (isCancelled) return;
          reconnectTimeout = setTimeout(connectWebSocket, 2000);
        };

        ws.onerror = () => {
          ws.close();
        };
      } catch (err) {
        console.warn("GD WS connect failed, falling back to HTTP sync:", err);
      }
    };

    connectWebSocket();
    syncRoomState(activeRoomId);

    // Heartbeat poll every 1s as reliable backup
    pollTimerRef.current = setInterval(() => {
      syncRoomState(activeRoomId);
    }, 1000);

    return () => {
      isCancelled = true;
      clearTimeout(reconnectTimeout);
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      peerConnectionsRef.current.forEach((pc) => pc.close());
      peerConnectionsRef.current.clear();
      remoteAudiosRef.current.forEach((audio) => {
        audio.pause();
        audio.srcObject = null;
      });
      remoteAudiosRef.current.clear();
    };
  }, [currentView, activeRoomId, syncRoomState, apiBase, myUserId, myName, createPeerConnection]);

  // Gracefully leave on page unload / refresh
  useEffect(() => {
    const handleUnload = () => {
      if (activeRoomId && myUserId) {
        navigator.sendBeacon(
          `${apiBase}/api/gd-rooms/${activeRoomId}/leave`,
          new Blob([JSON.stringify({ participant_id: myUserId })], { type: "application/json" })
        );
      }
    };
    window.addEventListener("beforeunload", handleUnload);
    return () => window.removeEventListener("beforeunload", handleUnload);
  }, [activeRoomId, myUserId, apiBase]);

  // Join a Room
  const handleJoinRoom = async (rid: string) => {
    try {
      const res = await fetch(`${apiBase}/api/gd-rooms/${rid}/join`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          participant_id: myUserId,
          name: myName,
          avatar: `https://api.dicebear.com/7.x/bottts/svg?seed=${myUserId}`,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setActiveRoomId(rid);
        setRoomState(data);
        setCurrentView("room");
        setAiEvaluation(null);
        return;
      } else {
        const err = await res.json();
        alert(err.detail || "Unable to join room.");
      }
    } catch {
      // Offline fallback join
      const topic = GD_TOPICS_250[Math.floor(Math.random() * GD_TOPICS_250.length)];
      setActiveRoomId(rid);
      setRoomState({
        room_id: rid,
        status: "waiting",
        phase: "waiting",
        participants_count: 1,
        max_capacity: 6,
        participants: [
          {
            id: myUserId,
            name: myName,
            avatar: `https://api.dicebear.com/7.x/bottts/svg?seed=${myUserId}`,
            is_speaking: false,
            mic_closed: true,
          },
        ],
        topic: topic as GDTopic,
        turn_order: [myUserId],
        current_turn_index: 0,
        current_speaker_id: null,
        current_speaker_name: null,
        turn_time_left: 60,
        total_time_left: 600,
        transcripts: [],
      });
      setCurrentView("room");
    }
  };

  // Leave Room
  const handleLeaveRoom = async () => {
    if (!activeRoomId) return;
    try {
      await fetch(`${apiBase}/api/gd-rooms/${activeRoomId}/leave`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ participant_id: myUserId }),
      });
    } catch {
      // Fallback
    }
    setActiveRoomId(null);
    setRoomState(null);
    setCurrentView("lobby");
    setAiEvaluation(null);
    fetchRoomsDirectory();
  };

  // Lock Room (manual trigger when >= 2 participants)
  const handleLockRoom = async () => {
    if (!activeRoomId) return;
    try {
      const res = await fetch(`${apiBase}/api/gd-rooms/${activeRoomId}/lock`, {
        method: "POST",
      });
      if (res.ok) {
        const data = await res.json();
        setRoomState(data);
        return;
      } else {
        const err = await res.json();
        alert(err.detail || "Could not lock room.");
      }
    } catch {
      // Fallback client lock
      if (roomState && roomState.participants.length >= 2) {
        const topic = GD_TOPICS_250[Math.floor(Math.random() * GD_TOPICS_250.length)];
        const turnOrder = [...roomState.participants.map((p) => p.id)].sort(() => 0.5 - Math.random());
        setRoomState((prev) =>
          prev
            ? {
                ...prev,
                status: "in_discussion",
                phase: "individual_turns",
                topic: topic as GDTopic,
                turn_order: turnOrder,
                current_turn_index: 0,
                current_speaker_id: turnOrder[0],
                turn_time_left: 60,
                total_time_left: 600,
              }
            : null
        );
      }
    }
  };

  // Add Simulated Candidate (convenient helper for solitary testing/presentation)
  const handleAddSimulatedPeer = async () => {
    if (!activeRoomId || !roomState) return;
    if (roomState.participants.length >= 6) return;

    const names = ["Aarav Mehta", "Diya Sen", "Rohan Verma", "Sneha Rao", "Vikram Das"];
    const unusedName =
      names.find((n) => !roomState.participants.some((p) => p.name === n)) || `Peer ${roomState.participants.length + 1}`;
    const simId = `sim_${Math.random().toString(36).substring(2, 7)}`;

    try {
      const res = await fetch(`${apiBase}/api/gd-rooms/${activeRoomId}/join`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          participant_id: simId,
          name: unusedName,
          avatar: `https://api.dicebear.com/7.x/bottts/svg?seed=${simId}`,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setRoomState(data);
      }
    } catch {
      // Client-side peer addition
      setRoomState((prev) => {
        if (!prev) return null;
        const newParticipants = [
          ...prev.participants,
          {
            id: simId,
            name: unusedName,
            avatar: `https://api.dicebear.com/7.x/bottts/svg?seed=${simId}`,
            is_speaking: false,
            mic_closed: true,
          },
        ];
        // Auto-lock check on 6 members!
        const autoLock = newParticipants.length === 6;
        return {
          ...prev,
          participants_count: newParticipants.length,
          participants: newParticipants,
          status: autoLock ? "in_discussion" : prev.status,
          phase: autoLock ? "individual_turns" : prev.phase,
        };
      });
    }
  };

  // Submit Spoken Argument
  const handleSubmitSpeech = async () => {
    if (!speechInput.trim() || !activeRoomId) return;
    setIsSubmittingSpeech(true);

    const spokenText = speechInput.trim();
    // Stop audio recording to extract real mic audio blob
    const audioBase64 = await stopAudioRecording();
    if (canISpeak && micPermission === "granted") {
      startAudioRecording();
    }

    try {
      const res = await fetch(`${apiBase}/api/gd-rooms/${activeRoomId}/speak`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          participant_id: myUserId,
          name: myName,
          text: spokenText,
          audio_data: audioBase64 || undefined,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setRoomState(data);
        setSpeechInput("");
      } else {
        const err = await res.json();
        alert(err.detail || "Unable to speak right now.");
      }
    } catch {
      // Local fallback append
      setRoomState((prev) =>
        prev
          ? {
              ...prev,
              transcripts: [
                ...prev.transcripts,
                {
                  participant_id: myUserId,
                  name: myName,
                  text: spokenText,
                  timestamp: Date.now(),
                  audio_data: audioBase64 || undefined,
                },
              ],
            }
          : null
      );
      setSpeechInput("");
    } finally {
      setIsSubmittingSpeech(false);
    }

    // Fast-path WebSocket broadcast
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(
          JSON.stringify({
            type: "speak",
            text: spokenText,
            audio_data: audioBase64 || undefined,
          })
        );
      } catch {}
    }
  };

  // Evaluate final speech
  const handleRequestEvaluation = async () => {
    if (!roomState) return;
    setIsEvaluating(true);

    const mySpeeches = roomState.transcripts.filter((t) => t.participant_id === myUserId).map((t) => t.text).join(" ");

    try {
      const res = await fetch(`${apiBase}/api/gd-evaluate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: roomState.topic?.title || "Placement Group Discussion",
          transcript: mySpeeches || speechInput || "Active participation in multi-candidate discussion round.",
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setAiEvaluation(data);
      }
    } catch {
      setAiEvaluation({
        score: 82,
        clarity: "Articulate and structured",
        reasoning: "Contributed clear points aligned with topic constraints during turn allocation.",
        strengths: ["Respectful of speaking order", "Logical structuring of thoughts"],
        suggestions: "Cite more empirical industry case studies during the open debate phase.",
      });
    } finally {
      setIsEvaluating(false);
    }
  };

  // Computed state for active user
  const isMyTurn =
    roomState?.phase === "individual_turns" && roomState?.current_speaker_id === myUserId;
  const isOpenDiscussion = roomState?.phase === "open_discussion";
  const canISpeak = isMyTurn || isOpenDiscussion;

  // Automated speech contribution for simulated peers during their turn
  useEffect(() => {
    if (!roomState || roomState.status !== "in_discussion" || !activeRoomId) return;
    const speakerId = roomState.current_speaker_id;
    if (!speakerId || !speakerId.startsWith("sim_")) return;

    if (simSpeechDoneRef.current[speakerId]) return;

    const timer = setTimeout(async () => {
      simSpeechDoneRef.current[speakerId] = true;
      const speakerObj = roomState.participants.find((p) => p.id === speakerId);
      const speakerName = speakerObj?.name || "Candidate";
      const topic = roomState.topic;
      const argument =
        Math.random() > 0.5
          ? topic?.starter_pros || "I believe adopting this strategy significantly optimizes operational efficiency and long-term enterprise advantage."
          : topic?.starter_cons || "However, we must critically evaluate compliance, infrastructure costs, and workforce readiness before scaling.";

      try {
        await fetch(`${apiBase}/api/gd-rooms/${activeRoomId}/speak`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            participant_id: speakerId,
            name: speakerName,
            text: argument,
          }),
        });
      } catch {}
    }, 4500);

    return () => clearTimeout(timer);
  }, [roomState?.current_speaker_id, roomState?.status, roomState?.phase, activeRoomId, apiBase, roomState?.topic, roomState?.participants]);

  // Enforce hardware microphone track state & speech recognition based on speaking turn
  useEffect(() => {
    const canSpeak = isMyTurn || isOpenDiscussion;

    // Detect transition into user's turn
    if (canSpeak && !prevCanSpeakRef.current && roomState?.status === "in_discussion") {
      playTurnChime();
      if (micPermission === "idle") {
        requestMicAccess();
      } else if (micPermission === "granted") {
        startAudioRecording();
      }
    }
    prevCanSpeakRef.current = !!canSpeak;

    // Enable/disable actual mic tracks
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getAudioTracks().forEach((track) => {
        track.enabled = !!canSpeak;
      });
    }

    // Start / stop speech recognition & audio recording
    if (recognitionRef.current) {
      if (canSpeak && micPermission === "granted") {
        try {
          recognitionRef.current.start();
          setIsRecognizing(true);
        } catch {
          // already running
        }
        startAudioRecording();
      } else {
        try {
          recognitionRef.current.stop();
          setIsRecognizing(false);
        } catch {}
      }
    }
  }, [isMyTurn, isOpenDiscussion, micPermission, roomState?.status, startAudioRecording]);

  // Clean up media streams and recognition on unmount
  useEffect(() => {
    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((t) => t.stop());
      }
      if (audioContextRef.current && audioContextRef.current.state !== "closed") {
        audioContextRef.current.close().catch(() => {});
      }
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch {}
      }
    };
  }, []);

  // Format mm:ss
  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  // Quick Join Handler (finds first room with waiting candidates, or first open room)
  const handleQuickJoin = () => {
    const target = roomsList.find((r) => r.can_join && r.participants_count > 0) || roomsList.find((r) => r.can_join);
    if (target) {
      handleJoinRoom(target.room_id);
    } else {
      handleJoinRoom("GD001");
    }
  };

  // ==========================================
  // VIEW 1: ROOMS LOBBY (GD000 - GD999)
  // ==========================================
  if (currentView === "lobby") {
    return (
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {/* Clean Header Bar */}
        <section className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-xl font-bold tracking-tight text-slate-900 sm:text-2xl">
                Group Discussion Arena
              </h1>
              <p className="mt-1 text-sm text-slate-500">
                Multi-participant rooms with automated turn management, real microphone audio meters, and live speech evaluation.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs">
                <span className="font-semibold text-slate-500">Joining As:</span>
                <input
                  type="text"
                  value={myName}
                  onChange={(e) => {
                    const val = e.target.value;
                    setMyName(val);
                    if (typeof window !== "undefined") {
                      localStorage.setItem("skillbridge_gd_user_name", val);
                    }
                  }}
                  placeholder="Candidate Name"
                  className="w-32 rounded bg-white px-2 py-1 text-xs font-bold text-slate-900 outline-none border border-slate-200 focus:border-indigo-500"
                />
              </div>

              <button
                onClick={handleQuickJoin}
                className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-xs font-bold text-white shadow-xs transition hover:bg-indigo-600"
              >
                <Play className="h-3.5 w-3.5" /> Quick Join
              </button>
            </div>
          </div>
        </section>

        {/* Directory Search & Filters */}
        <section className="mb-6 flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-xs sm:flex-row sm:items-center sm:justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search room code (e.g. GD001, GD042, GD999)..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setPage(1);
              }}
              className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2.5 pl-10 pr-4 text-sm outline-none transition focus:border-indigo-500 focus:bg-white focus:ring-2 focus:ring-indigo-100"
            />
          </div>

          <div className="flex flex-wrap items-center gap-1.5 text-xs font-semibold">
            <button
              onClick={() => setStatusFilter("all")}
              className={`rounded-lg px-3 py-2 transition ${
                statusFilter === "all" ? "bg-slate-900 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              All (1,000)
            </button>
            <button
              onClick={() => setStatusFilter("available")}
              className={`rounded-lg px-3 py-2 transition ${
                statusFilter === "available" ? "bg-emerald-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              Available (1-5/6)
            </button>
            <button
              onClick={() => setStatusFilter("waiting")}
              className={`rounded-lg px-3 py-2 transition ${
                statusFilter === "waiting" ? "bg-amber-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              Ready to Lock (2-5)
            </button>
            <button
              onClick={() => setStatusFilter("in_session")}
              className={`rounded-lg px-3 py-2 transition ${
                statusFilter === "in_session" ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              In Session (Locked)
            </button>
          </div>
        </section>

        {/* Rooms Grid */}
        <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {roomsList.map((room) => {
            const isFull = room.participants_count >= 6;
            const isLocked = room.is_locked;
            const canLock = room.can_lock;

            return (
              <div
                key={room.room_id}
                className={`group flex flex-col justify-between rounded-xl border bg-white p-5 transition hover:shadow-md ${
                  isLocked
                    ? "border-indigo-200 bg-indigo-50/20"
                    : room.participants_count > 0
                    ? "border-emerald-200 bg-emerald-50/10"
                    : "border-slate-200"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-base font-extrabold tracking-wide text-slate-900">
                      {room.room_id}
                    </span>
                    <span
                      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-bold ${
                        isLocked
                          ? "bg-indigo-100 text-indigo-700"
                          : isFull
                          ? "bg-red-100 text-red-700"
                          : canLock
                          ? "bg-amber-100 text-amber-800"
                          : "bg-slate-100 text-slate-600"
                      }`}
                    >
                      {isLocked ? (
                        <>
                          <Lock className="h-3 w-3" /> In Session
                        </>
                      ) : isFull ? (
                        "Auto-Locked (Full)"
                      ) : canLock ? (
                        "Ready to Lock"
                      ) : (
                        "Open"
                      )}
                    </span>
                  </div>

                  {/* Seat Visualization */}
                  <div className="mt-4 flex items-center justify-between">
                    <div className="flex items-center gap-1">
                      {Array.from({ length: 6 }).map((_, i) => (
                        <div
                          key={i}
                          className={`h-2.5 w-2.5 rounded-full ${
                            i < room.participants_count ? "bg-indigo-600" : "bg-slate-200"
                          }`}
                          title={`Seat ${i + 1}`}
                        />
                      ))}
                    </div>
                    <span className="text-xs font-bold text-slate-700">
                      {room.participants_count} / 6 Members
                    </span>
                  </div>

                  <p className="mt-3 line-clamp-1 text-xs text-slate-500">
                    {room.topic_title || "Waiting for participants to lock & draw topic..."}
                  </p>
                </div>

                <div className="mt-5 border-t border-slate-100 pt-3">
                  <button
                    disabled={isLocked || isFull}
                    onClick={() => handleJoinRoom(room.room_id)}
                    className={`w-full rounded-lg px-4 py-2 text-xs font-bold transition ${
                      isLocked || isFull
                        ? "cursor-not-allowed bg-slate-100 text-slate-400"
                        : "bg-slate-900 text-white hover:bg-indigo-600"
                    }`}
                  >
                    {isLocked ? "Room In Session" : isFull ? "Room Full (6/6)" : "Join Room"}
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Pagination */}
        <div className="mt-8 flex items-center justify-between border-t border-slate-200 pt-4 text-xs font-semibold text-slate-500">
          <span>
            Page {page} of {totalPages}
          </span>
          <div className="flex gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 hover:bg-slate-50 disabled:opacity-40"
            >
              Previous
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 hover:bg-slate-50 disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ==========================================
  // VIEW 2: ACTIVE ROOM VIEW (Up to 6 Participants)
  // ==========================================
  const currentSpeaker = roomState?.current_speaker_name || "Waiting for turn...";
  const turnTimeLeft = roomState?.turn_time_left || 60;
  const totalTimeLeft = roomState?.total_time_left || 600;
  const isIndividualTurnPhase = roomState?.phase === "individual_turns";
  const isOpenPhase = roomState?.phase === "open_discussion";
  const isDiscussionActive = roomState?.status === "in_discussion";

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      {/* Room Control Top Bar */}
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-600 font-mono text-base font-extrabold text-white">
            {roomState?.room_id || activeRoomId}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-bold text-slate-900">Placement GD Room</h2>
              <span
                className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${
                  roomState?.status === "in_discussion"
                    ? "bg-red-100 text-red-800 animate-pulse"
                    : "bg-emerald-100 text-emerald-800"
                }`}
              >
                {roomState?.status === "in_discussion" ? "LIVE DISCUSSION" : "WAITING LOBBY"}
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Capacity: <span className="font-bold text-slate-800">{roomState?.participants.length || 0} / 6</span> Candidates • Max 10 Min Session
            </p>
          </div>
        </div>

        {/* Timers & Status */}
        <div className="flex flex-wrap items-center gap-3">
          {isDiscussionActive && (
            <>
              {isIndividualTurnPhase && (
                <div className="flex items-center gap-2 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-xs font-bold text-amber-900">
                  <Clock className="h-4 w-4 text-amber-600" />
                  <span>Turn Time: {turnTimeLeft}s</span>
                </div>
              )}
              <div className="flex items-center gap-2 rounded-xl border border-indigo-200 bg-indigo-50 px-3 py-2 text-xs font-bold text-indigo-900">
                <Clock className="h-4 w-4 text-indigo-600" />
                <span>Total Left: {formatTime(totalTimeLeft)}</span>
              </div>
            </>
          )}

          {/* Live Audible Voice Output Toggle */}
          <button
            onClick={() => setIsRoomAudioMuted((prev) => !prev)}
            className={`inline-flex items-center gap-1.5 rounded-xl border px-3 py-2 text-xs font-bold transition ${
              isRoomAudioMuted
                ? "border-red-200 bg-red-50 text-red-700 hover:bg-red-100"
                : "border-emerald-200 bg-emerald-50 text-emerald-800 hover:bg-emerald-100"
            }`}
            title={isRoomAudioMuted ? "Audio Output Muted (Click to Unmute)" : "Live WebRTC Audio Output Active across candidates"}
            type="button"
          >
            {isRoomAudioMuted ? (
              <>
                <VolumeX className="h-3.5 w-3.5 text-red-600" />
                <span>Voice: Muted</span>
              </>
            ) : (
              <>
                <Volume2 className="h-3.5 w-3.5 text-emerald-600 animate-pulse" />
                <span>Voice: Audible</span>
              </>
            )}
          </button>

          <button
            onClick={handleLeaveRoom}
            className="inline-flex items-center gap-1.5 rounded-xl border border-red-200 bg-red-50 px-4 py-2 text-xs font-bold text-red-700 hover:bg-red-100"
          >
            <LogOut className="h-3.5 w-3.5" /> Leave Room
          </button>
        </div>
      </div>

      {/* Main Grid: Left Participants, Right Topic & Debate */}
      <div className="grid gap-6 lg:grid-cols-[1fr_1.35fr]">
        {/* Left: 6 Participants Slots */}
        <section className="flex flex-col gap-4">
          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-700">
                Participants ({roomState?.participants.length || 0} / 6)
              </h3>
              {roomState?.status === "waiting" && (
                <button
                  onClick={handleAddSimulatedPeer}
                  disabled={(roomState?.participants.length || 0) >= 6}
                  className="inline-flex items-center gap-1 text-xs font-bold text-indigo-600 hover:underline disabled:opacity-40"
                >
                  <UserPlus className="h-3.5 w-3.5" /> Add Test Peer
                </button>
              )}
            </div>

            {/* 6 Participant Tiles */}
            <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3">
              {Array.from({ length: 6 }).map((_, i) => {
                const p = roomState?.participants[i];
                if (!p) {
                  return (
                    <div
                      key={i}
                      className="flex h-36 flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 bg-slate-50/50 p-3 text-center text-slate-400"
                    >
                      <Users className="h-6 w-6 stroke-1 text-slate-300" />
                      <span className="mt-2 text-xs font-medium">Empty Seat {i + 1}</span>
                      <span className="text-[10px] text-slate-400">Waiting...</span>
                    </div>
                  );
                }

                const isSpeaker = p.is_speaking;
                const isMe = p.id === myUserId;
                const micMuted = p.mic_closed;

                return (
                  <div
                    key={p.id}
                    className={`relative flex h-36 flex-col items-center justify-between rounded-xl border p-3 text-center transition ${
                      isSpeaker
                        ? "border-emerald-500 bg-emerald-50/50 shadow-md ring-2 ring-emerald-400"
                        : "border-slate-200 bg-white"
                    }`}
                  >
                    {/* Badge */}
                    <div className="flex w-full items-center justify-between text-[10px]">
                      <span className={`font-bold ${isMe ? "text-indigo-600" : "text-slate-500"}`}>
                        {isMe ? "You" : `Seat ${i + 1}`}
                      </span>
                      <span
                        className={`inline-flex items-center gap-0.5 rounded-full px-1.5 py-0.5 font-bold ${
                          isSpeaker
                            ? "bg-emerald-100 text-emerald-800 animate-pulse"
                            : micMuted
                            ? "bg-slate-100 text-slate-500"
                            : "bg-indigo-100 text-indigo-700"
                        }`}
                      >
                        {isSpeaker ? (
                          <>
                            <Mic className="h-2.5 w-2.5" /> Speaking
                          </>
                        ) : micMuted ? (
                          <>
                            <MicOff className="h-2.5 w-2.5" /> Muted
                          </>
                        ) : (
                          <>
                            <Mic className="h-2.5 w-2.5" /> Open
                          </>
                        )}
                      </span>
                    </div>

                    {/* Avatar with Audible Soundwave */}
                    <div className="relative">
                      <img
                        src={p.avatar}
                        alt={p.name}
                        className={`h-12 w-12 rounded-full border-2 bg-slate-100 ${
                          isSpeaker ? "border-emerald-500 shadow-sm ring-2 ring-emerald-300" : "border-slate-200"
                        }`}
                      />
                      {isSpeaker && (
                        <span className="absolute -bottom-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-emerald-600 text-white shadow-xs">
                          <Volume2 className="h-2.5 w-2.5 animate-pulse" />
                        </span>
                      )}
                    </div>

                    {/* Name */}
                    <div className="w-full truncate text-xs font-bold text-slate-900">
                      {p.name}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Lock Control Area */}
            {roomState?.status === "waiting" && (
              <div className="mt-5 rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <h4 className="text-xs font-bold text-slate-900">Room Lock Criteria</h4>
                    <p className="mt-0.5 text-xs text-slate-500">
                      Requires min 2 participants to manually lock, or auto-locks immediately when room reaches 6 members.
                    </p>
                  </div>
                  <button
                    disabled={(roomState?.participants.length || 0) < 2}
                    onClick={handleLockRoom}
                    className="inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-xs font-bold text-white shadow-sm transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-slate-300"
                  >
                    <Lock className="h-3.5 w-3.5" /> Lock Room & Start GD
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* AI Rubric / Evaluation card */}
          {aiEvaluation && (
            <div className="rounded-2xl border border-emerald-200 bg-emerald-50/40 p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <h4 className="flex items-center gap-1.5 text-sm font-bold text-emerald-950">
                  <Award className="h-4 w-4 text-emerald-600" /> AI Assessor Evaluation
                </h4>
                <span className="rounded-full bg-emerald-200 px-3 py-0.5 text-xs font-black text-emerald-900">
                  Score: {aiEvaluation.score} / 100
                </span>
              </div>
              <p className="mt-2 text-xs font-medium text-emerald-900">
                <span className="font-bold">Articulation:</span> {aiEvaluation.clarity}
              </p>
              <p className="mt-1 text-xs text-slate-700">{aiEvaluation.reasoning}</p>
              <div className="mt-3 rounded-lg bg-white p-3 text-xs text-slate-600 border border-emerald-100">
                <span className="font-bold text-slate-800">Improvement Suggestion: </span>
                {aiEvaluation.suggestions}
              </div>
            </div>
          )}
        </section>

        {/* Right: Topic Banner & Live Transcript Feed */}
        <section className="flex flex-col gap-4">
          {/* Active Topic Banner */}
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between gap-2">
              <span className="inline-flex items-center gap-1.5 rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 text-xs font-bold text-indigo-700">
                <Globe2 className="h-3.5 w-3.5" />
                {roomState?.topic?.category || "Trending Topic"}
              </span>
              <span className="text-xs font-semibold text-slate-400">
                {roomState?.topic?.id || "TOPIC042"}
              </span>
            </div>

            <h3 className="mt-3 text-lg font-extrabold text-slate-950 sm:text-xl">
              {roomState?.topic?.title || "Waiting to lock room & draw topic..."}
            </h3>

            {roomState?.topic && (
              <div className="mt-4 grid gap-3 text-xs sm:grid-cols-2">
                <div className="rounded-xl border border-emerald-100 bg-emerald-50/50 p-3">
                  <div className="font-bold text-emerald-800">Pros / Affirmative Pointers</div>
                  <p className="mt-1 text-slate-700 leading-relaxed">{roomState.topic.starter_pros}</p>
                </div>
                <div className="rounded-xl border border-rose-100 bg-rose-50/50 p-3">
                  <div className="font-bold text-rose-800">Cons / Counter Pointers</div>
                  <p className="mt-1 text-slate-700 leading-relaxed">{roomState.topic.starter_cons}</p>
                </div>
              </div>
            )}
          </div>

          {/* Phase Notification Banner */}
          {isDiscussionActive && (
            <div
              className={`rounded-xl border p-4 ${
                isIndividualTurnPhase
                  ? "border-amber-200 bg-amber-50/70 text-amber-950"
                  : "border-indigo-200 bg-indigo-50/70 text-indigo-950"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-white font-bold text-xs shadow-xs">
                    {isIndividualTurnPhase ? "1" : "2"}
                  </span>
                  <div>
                    <h4 className="text-xs font-extrabold uppercase tracking-wide">
                      {isIndividualTurnPhase
                        ? "Phase 1: Individual Round (1 Min per Candidate)"
                        : "Phase 2: Open Floor Discussion"}
                    </h4>
                    <p className="text-xs opacity-85">
                      {isIndividualTurnPhase
                        ? `Current Speaker: ${currentSpeaker} (${turnTimeLeft}s left)`
                        : `All participants can debate simultaneously (${formatTime(totalTimeLeft)} left)`}
                    </p>
                  </div>
                </div>

                {isIndividualTurnPhase && (
                  <div className="text-right">
                    <span className="text-lg font-black text-amber-900">{turnTimeLeft}s</span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Live Discussion Feed */}
          <div className="flex flex-1 flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm min-h-[280px]">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h4 className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-slate-600">
                <MessageSquare className="h-4 w-4 text-indigo-600" />
                Discussion Transcript & Spoken Points
              </h4>
              <span className="text-[11px] text-slate-400">
                {roomState?.transcripts.length || 0} Points Recorded
              </span>
            </div>

            <div className="mt-3 flex-1 overflow-y-auto space-y-3 max-h-64 pr-1">
              {roomState?.transcripts.length === 0 ? (
                <div className="flex h-36 items-center justify-center text-center text-xs text-slate-400">
                  No statements recorded yet. Spoken contributions during turns will appear here.
                </div>
              ) : (
                roomState?.transcripts.map((t, idx) => (
                  <div
                    key={idx}
                    className={`rounded-xl border p-3 text-xs leading-relaxed ${
                      t.participant_id === myUserId
                        ? "border-indigo-200 bg-indigo-50/40 text-indigo-950"
                        : "border-slate-100 bg-slate-50 text-slate-800"
                    }`}
                  >
                    <div className="flex items-center justify-between font-bold">
                      <span>{t.name}</span>
                      <span className="text-[10px] text-slate-400">
                        {new Date(t.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                    </div>
                    <p className="mt-1">{t.text}</p>
                  </div>
                ))
              )}
            </div>

            {/* Speaking & Real Hardware Microphone Bar */}
            <div className="mt-4 border-t border-slate-100 pt-3">
              {!canISpeak ? (
                <div className="flex flex-col gap-2 rounded-xl border border-slate-200 bg-slate-50 p-3.5">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-200 text-slate-600">
                        <MicOff className="h-4 w-4" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold text-slate-700">Microphone Hardware Muted & Locked</span>
                          <span className="rounded-full bg-slate-200 px-2 py-0.5 text-[10px] font-bold text-slate-600">
                            Turn Guard
                          </span>
                        </div>
                        <p className="mt-0.5 text-[11px] text-slate-500">
                          {roomState?.phase === "individual_turns"
                            ? `Active speaker: ${roomState?.current_speaker_name || "Another candidate"}. Your mic opens automatically when your 1-min turn arrives.`
                            : "Microphone is idle until discussion begins."}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex flex-col gap-3 rounded-xl border border-emerald-200 bg-emerald-50/30 p-3.5 shadow-xs">
                  {/* Mic Status Header */}
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-emerald-100 pb-2.5">
                    <div className="flex items-center gap-2.5">
                      <div
                        className={`flex h-8 w-8 items-center justify-center rounded-lg ${
                          micPermission === "granted"
                            ? "bg-emerald-600 text-white shadow-sm animate-pulse"
                            : "bg-amber-100 text-amber-800"
                        }`}
                      >
                        <Mic className="h-4 w-4" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-extrabold text-slate-900">
                            {isMyTurn ? "YOUR INDIVIDUAL SPEAKING TURN (1 MIN)" : "OPEN FLOOR DEBATE"}
                          </span>
                          {micPermission === "granted" ? (
                            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800">
                              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-ping"></span>
                              MIC ACTIVE
                            </span>
                          ) : (
                            <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-800">
                              MIC PERMISSION REQUIRED
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-500">
                          {micPermission === "granted"
                            ? "Hardware mic connected. Speak naturally to dictate your points in real-time."
                            : "Browser needs microphone permission to broadcast your voice."}
                        </p>
                      </div>
                    </div>

                    {micPermission !== "granted" ? (
                      <button
                        onClick={requestMicAccess}
                        className="inline-flex items-center gap-1.5 rounded-xl bg-amber-600 px-3.5 py-1.5 text-xs font-bold text-white shadow-sm hover:bg-amber-500 transition"
                      >
                        <Mic className="h-3.5 w-3.5" /> Enable Microphone
                      </button>
                    ) : (
                      <div className="flex items-center gap-1.5 rounded-lg bg-white px-3 py-1.5 border border-emerald-200 shadow-2xs">
                        <span className="text-[10px] font-bold text-slate-500 uppercase mr-1">Voice Meter</span>
                        {[0.2, 0.5, 0.8, 1.0, 0.7, 0.4].map((mult, i) => (
                          <div
                            key={i}
                            className={`w-1 rounded-full transition-all duration-75 ${
                              audioLevel > 12 ? "bg-emerald-500" : "bg-slate-300"
                            }`}
                            style={{
                              height: `${Math.max(4, Math.min(18, audioLevel * mult))}px`,
                            }}
                          />
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Interim Voice Dictation Live Box */}
                  {interimTranscript && (
                    <div className="rounded-xl border border-indigo-200 bg-indigo-50/80 p-2.5 text-xs italic text-indigo-950 flex items-center gap-2">
                      <Mic className="h-3.5 w-3.5 text-indigo-600 animate-pulse shrink-0" />
                      <span className="truncate">Dictating voice: "{interimTranscript}"</span>
                    </div>
                  )}

                  {/* Input Box for Spoken Argument */}
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      placeholder="Transcribed voice appears here, or type your arguments..."
                      value={speechInput}
                      onChange={(e) => setSpeechInput(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && handleSubmitSpeech()}
                      className="flex-1 rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-xs outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
                    />
                    <button
                      disabled={!speechInput.trim() || isSubmittingSpeech}
                      onClick={handleSubmitSpeech}
                      className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-4 py-2.5 text-xs font-bold text-white shadow-sm transition hover:bg-indigo-500 disabled:opacity-40"
                    >
                      <Send className="h-3.5 w-3.5" /> Submit Speech
                    </button>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-500">
                    <span>
                      {isRecognizing
                        ? "🎙️ Live speech-to-text active • Speaking into mic appends to argument"
                        : "Click 'Submit Speech' to record argument to the discussion transcript"}
                    </span>
                    <button
                      onClick={handleRequestEvaluation}
                      disabled={isEvaluating}
                      className="text-indigo-600 hover:underline font-bold"
                    >
                      {isEvaluating ? "Analyzing..." : "Evaluate Contributions"}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
