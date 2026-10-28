"use client";

import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import dynamic from "next/dynamic";
import {
  Code2,
  Play,
  RotateCcw,
  Terminal,
  CheckCircle2,
  XCircle,
  Copy,
  Check,
  Users,
  Search,
  LogOut,
  Send,
  MessageSquare,
  FileCode,
  Layers,
  Sparkles,
  Zap,
} from "lucide-react";

// Dynamically import Monaco Editor to prevent Next.js SSR hydration mismatches
const MonacoEditor = dynamic(() => import("@monaco-editor/react"), {
  ssr: false,
  loading: () => (
    <div className="flex h-96 w-full items-center justify-center rounded-xl bg-slate-900 font-mono text-xs text-slate-400">
      Loading Monaco Editor...
    </div>
  ),
});

export type SupportedLang = "python" | "javascript" | "java" | "cpp";

export type CodeParticipant = {
  id: string;
  name: string;
  avatar: string;
  joined_at?: number;
  last_seen?: number;
};

export type CodeChatMessage = {
  id: string;
  sender_id: string;
  sender_name: string;
  text: string;
  timestamp: number;
};

export type CodeRoomSummary = {
  room_id: string;
  title: string;
  participants_count: number;
  max_capacity: number;
  language: string;
  challenge_id?: string;
  last_run_status?: string | null;
  can_join: boolean;
};

export type CodeRoomState = {
  room_id: string;
  title: string;
  participants: CodeParticipant[];
  max_capacity: number;
  language: SupportedLang;
  challenge_id?: string;
  code: string;
  terminal_output?: string | null;
  last_run_status?: string | null;
  last_run_by?: string | null;
  last_run_time?: number | null;
  messages: CodeChatMessage[];
};

export const DEFAULT_TEMPLATES: Record<SupportedLang, string> = {
  python: `# SkillBridge Python 3.12 Collaborative Workspace
def main():
    print("Real-time collaborative session active on Port 8000")

if __name__ == "__main__":
    main()
`,
  javascript: `// SkillBridge JavaScript (Node.js 24) Collaborative Workspace
function main() {
    console.log("Real-time collaborative session active on Port 8000");
}

main();
`,
  java: `// SkillBridge OpenJDK 21 Collaborative Workspace
import java.util.*;

public class Main {
    public static void main(String[] args) {
        System.out.println("Real-time collaborative session active on Port 8000");
    }
}
`,
  cpp: `// SkillBridge C++ (MinGW 15) Collaborative Workspace
#include <iostream>
using namespace std;

int main() {
    cout << "Real-time collaborative session active on Port 8000" << endl;
    return 0;
}
`,
};

function getWsUrl(apiBase: string, roomId: string, userId: string, userName: string): string {
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
    host = raw.replace(/\/.*$/, "");
    protocol = "ws:";
  } else if (apiBase.startsWith("https://")) {
    const raw = apiBase.replace("https://", "");
    host = raw.replace(/\/.*$/, "");
    protocol = "wss:";
  }
  return `${protocol}//${host}/ws/code/${roomId}?participant_id=${userId}&name=${encodeURIComponent(userName)}`;
}

interface CodeStudioProps {
  apiBase: string;
  candidateName?: string;
}

export default function CodeStudio({ apiBase, candidateName }: CodeStudioProps) {
  // Unique client connection ID per browser tab so multiple tabs are never confused
  const myClientId = useRef(
    typeof window !== "undefined"
      ? `client_${Math.random().toString(36).substring(2, 9)}_${Date.now()}`
      : "client_default"
  ).current;

  // Session-isolated user ID (each tab gets a distinct participant identity)
  const [myUserId] = useState(() => {
    if (typeof window !== "undefined") {
      let stored = sessionStorage.getItem("skillbridge_code_session_id");
      if (!stored) {
        stored = `coder_${Math.random().toString(36).substring(2, 9)}`;
        sessionStorage.setItem("skillbridge_code_session_id", stored);
      }
      return stored;
    }
    return `coder_${Math.random().toString(36).substring(2, 9)}`;
  });

  const [myName, setMyName] = useState(() => {
    if (typeof window !== "undefined") {
      let storedName = sessionStorage.getItem("skillbridge_code_session_name");
      if (storedName) return storedName;
      if (candidateName) return candidateName;
      const randNum = Math.floor(Math.random() * 899) + 100;
      const autoName = `Coder-${randNum}`;
      sessionStorage.setItem("skillbridge_code_session_name", autoName);
      return autoName;
    }
    return candidateName || "Developer";
  });

  // Views: "lobby" (rooms directory) | "room" (active collaborative workspace)
  const [currentView, setCurrentView] = useState<"lobby" | "room">("lobby");
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "active" | "available">("all");
  const [roomsList, setRoomsList] = useState<CodeRoomSummary[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(21);

  // Active room workspace state
  const [activeRoomId, setActiveRoomId] = useState<string | null>(null);
  const [roomState, setRoomState] = useState<CodeRoomState | null>(null);
  const [language, setLanguage] = useState<SupportedLang>("python");
  const [code, setCode] = useState<string>(DEFAULT_TEMPLATES.python);
  const [isRunning, setIsRunning] = useState(false);
  const [terminalOutput, setTerminalOutput] = useState<string | null>(null);
  const [runSuccess, setRunSuccess] = useState<boolean | null>(null);
  const [copied, setCopied] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [isSendingChat, setIsSendingChat] = useState(false);
  const [syncStatus, setSyncStatus] = useState<"synced" | "saving">("synced");

  // Real-Time WebSocket & Peer State
  const [wsConnected, setWsConnected] = useState(false);
  const [lastPeerEdit, setLastPeerEdit] = useState<{ name: string; timestamp: number } | null>(null);
  const [peerCursors, setPeerCursors] = useState<
    Record<string, { name: string; lineNumber: number; column: number; timestamp: number }>
  >({});

  const wsRef = useRef<WebSocket | null>(null);
  const editorRef = useRef<any>(null);
  const isRemoteUpdatingRef = useRef<boolean>(false);
  const lastCursorSendRef = useRef<number>(0);
  const pollTimerRef = useRef<NodeJS.Timeout | null>(null);
  const debounceSyncRef = useRef<NodeJS.Timeout | null>(null);
  const chatBottomRef = useRef<HTMLDivElement | null>(null);

  // 1. Fetch Rooms Directory
  const fetchRoomsDirectory = useCallback(async () => {
    try {
      const q = new URLSearchParams({
        page: page.toString(),
        limit: "24",
      });
      if (searchQuery.trim()) q.set("search", searchQuery.trim());
      if (statusFilter !== "all") q.set("status_filter", statusFilter);

      const res = await fetch(`${apiBase}/api/code-rooms?${q.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setRoomsList(data.rooms || []);
        setTotalPages(Math.ceil((data.total_rooms || 500) / 24));
        return;
      }
    } catch {}

    // Clean fallback for CODE000 - CODE499
    const fallbackRooms: CodeRoomSummary[] = Array.from({ length: 24 }).map((_, i) => {
      const idx = (page - 1) * 24 + i;
      const rid = `CODE${idx.toString().padStart(3, "0")}`;
      return {
        room_id: rid,
        title: `Workspace ${rid}`,
        participants_count: 0,
        max_capacity: 8,
        language: "python",
        last_run_status: null,
        can_join: true,
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

  // 2. Process incoming WebSocket Messages
  const handleWsMessage = useCallback(
    (data: any) => {
      const type = data.type;

      if (type === "room_state") {
        const state: CodeRoomState = data.state;
        setRoomState(state);
        if (state.language) setLanguage(state.language);
        if (state.terminal_output !== undefined) setTerminalOutput(state.terminal_output);
        if (state.last_run_status !== undefined) setRunSuccess(state.last_run_status === "success");

        if (state.code) {
          setCode(state.code);
          if (editorRef.current) {
            const editor = editorRef.current;
            const model = editor.getModel();
            if (model && model.getValue() !== state.code) {
              isRemoteUpdatingRef.current = true;
              editor.setValue(state.code);
              isRemoteUpdatingRef.current = false;
            }
          }
        }
      } else if (type === "code_change") {
        // Accept code change from any other client/tab
        const isFromOther = data.client_id ? data.client_id !== myClientId : data.sender_id !== myUserId;
        if (isFromOther && data.code !== undefined) {
          const newCode = data.code;
          if (data.sender_name) {
            setLastPeerEdit({ name: data.sender_name, timestamp: Date.now() });
          }
          setCode(newCode);

          // Smoothly update Monaco model via executeEdits without losing local cursor
          if (editorRef.current) {
            const editor = editorRef.current;
            const model = editor.getModel();
            if (model && model.getValue() !== newCode) {
              const pos = editor.getPosition();
              const selections = editor.getSelections();

              isRemoteUpdatingRef.current = true;
              editor.executeEdits("remote-peer", [
                {
                  range: model.getFullModelRange(),
                  text: newCode,
                  forceMoveMarkers: true,
                },
              ]);

              if (pos) editor.setPosition(pos);
              if (selections) editor.setSelections(selections);
              isRemoteUpdatingRef.current = false;
            }
          }

          if (data.language && data.language !== language) {
            setLanguage(data.language);
          }
        }
      } else if (type === "cursor_update") {
        const isFromOther = data.client_id ? data.client_id !== myClientId : data.sender_id !== myUserId;
        if (isFromOther && data.cursor) {
          const peerKey = data.client_id || data.sender_id;
          setPeerCursors((prev) => ({
            ...prev,
            [peerKey]: {
              name: data.sender_name || "Peer",
              lineNumber: data.cursor.lineNumber,
              column: data.cursor.column,
              timestamp: Date.now(),
            },
          }));
        }
      } else if (type === "language_change") {
        const isFromOther = data.client_id ? data.client_id !== myClientId : data.sender_id !== myUserId;
        if (isFromOther) {
          setLanguage(data.language);
          if (data.code !== undefined) {
            setCode(data.code);
            if (editorRef.current) {
              const editor = editorRef.current;
              const model = editor.getModel();
              if (model && model.getValue() !== data.code) {
                isRemoteUpdatingRef.current = true;
                editor.executeEdits("remote-lang", [
                  {
                    range: model.getFullModelRange(),
                    text: data.code,
                    forceMoveMarkers: true,
                  },
                ]);
                isRemoteUpdatingRef.current = false;
              }
            }
          }
          setLastPeerEdit({
            name: `${data.sender_name || "Peer"} (switched to ${data.language})`,
            timestamp: Date.now(),
          });
        }
      } else if (type === "chat_message") {
        if (data.messages) {
          setRoomState((prev) => (prev ? { ...prev, messages: data.messages } : prev));
        } else if (data.message) {
          setRoomState((prev) => {
            if (!prev) return prev;
            const exists = prev.messages.some((m) => m.id === data.message.id);
            if (exists) return prev;
            return {
              ...prev,
              messages: [...prev.messages, data.message],
            };
          });
        }
      } else if (type === "code_run_started") {
        const isFromOther = data.client_id ? data.client_id !== myClientId : data.sender_id !== myUserId;
        if (isFromOther) {
          setIsRunning(true);
          setTerminalOutput(`▶️ ${data.sender_name || "Peer"} is executing ${data.language?.toUpperCase() || ""} code...\n`);
        }
      } else if (type === "code_run_result") {
        setIsRunning(false);
        setTerminalOutput(data.terminal_output || null);
        setRunSuccess(data.last_run_status === "success");
        if (data.messages) {
          setRoomState((prev) => (prev ? { ...prev, messages: data.messages } : prev));
        }
      } else if (type === "peer_joined" || type === "peer_left") {
        if (data.participants) {
          setRoomState((prev) => (prev ? { ...prev, participants: data.participants } : prev));
        }
      }
    },
    [myClientId, myUserId, language]
  );

  // 3. Connect WebSocket for Real-Time Synchronization in Active Room
  useEffect(() => {
    if (currentView !== "room" || !activeRoomId) {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      setWsConnected(false);
      return;
    }

    let isCancelled = false;
    let reconnectTimeout: NodeJS.Timeout | null = null;

    const connectWebSocket = () => {
      if (isCancelled) return;
      try {
        const wsUrl = getWsUrl(apiBase, activeRoomId, myUserId, myName);
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          if (isCancelled) return;
          setWsConnected(true);
        };

        ws.onmessage = (event) => {
          if (isCancelled) return;
          try {
            const data = JSON.parse(event.data);
            handleWsMessage(data);
          } catch (e) {
            console.error("WS Parse error:", e);
          }
        };

        ws.onclose = () => {
          if (isCancelled) return;
          setWsConnected(false);
          reconnectTimeout = setTimeout(connectWebSocket, 2000);
        };

        ws.onerror = () => {
          ws.close();
        };
      } catch (err) {
        console.warn("WS connect failed, relying on polling fallback:", err);
      }
    };

    connectWebSocket();

    // Heartbeat every 10 seconds
    const heartbeatTimer = setInterval(() => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: "heartbeat", participant_id: myUserId, client_id: myClientId }));
      }
    }, 10000);

    return () => {
      isCancelled = true;
      clearInterval(heartbeatTimer);
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      setWsConnected(false);
    };
  }, [currentView, activeRoomId, apiBase, myUserId, myName, myClientId, handleWsMessage]);

  // 4. Polling Fallback (in case WebSocket is blocked or offline)
  const syncRoomStateHttp = useCallback(
    async (rid: string) => {
      try {
        const res = await fetch(`${apiBase}/api/code-rooms/${rid}/state?participant_id=${myUserId}`);
        if (res.ok) {
          const data: CodeRoomState = await res.json();
          setRoomState(data);
          if (data.terminal_output !== undefined && !isRunning) {
            setTerminalOutput(data.terminal_output);
          }
          if (data.last_run_status !== undefined) {
            setRunSuccess(data.last_run_status === "success");
          }
        }
      } catch {}
    },
    [apiBase, myUserId, isRunning]
  );

  useEffect(() => {
    if (currentView === "room" && activeRoomId) {
      pollTimerRef.current = setInterval(() => {
        if (!wsConnected) {
          syncRoomStateHttp(activeRoomId);
        }
      }, 3000);

      return () => {
        if (pollTimerRef.current) clearInterval(pollTimerRef.current);
      };
    }
  }, [currentView, activeRoomId, wsConnected, syncRoomStateHttp]);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [roomState?.messages]);

  // Leave room gracefully on page unload
  useEffect(() => {
    const handleUnload = () => {
      if (activeRoomId && myUserId) {
        navigator.sendBeacon(
          `${apiBase}/api/code-rooms/${activeRoomId}/leave`,
          new Blob([JSON.stringify({ participant_id: myUserId })], { type: "application/json" })
        );
      }
    };
    window.addEventListener("beforeunload", handleUnload);
    return () => window.removeEventListener("beforeunload", handleUnload);
  }, [activeRoomId, myUserId, apiBase]);

  // Join Room
  const handleJoinRoom = async (rid: string) => {
    try {
      const res = await fetch(`${apiBase}/api/code-rooms/${rid}/join`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          participant_id: myUserId,
          name: myName,
          avatar: `https://api.dicebear.com/7.x/bottts/svg?seed=${myUserId}`,
        }),
      });

      if (res.ok) {
        const data: CodeRoomState = await res.json();
        setActiveRoomId(rid);
        setRoomState(data);
        const l = data.language || "python";
        setLanguage(l);
        setCode(data.code || DEFAULT_TEMPLATES[l]);
        setTerminalOutput(data.terminal_output || null);
        setRunSuccess(data.last_run_status ? data.last_run_status === "success" : null);
        setCurrentView("room");
        return;
      }
    } catch {}

    // Fallback join
    setActiveRoomId(rid);
    setLanguage("python");
    setCode(DEFAULT_TEMPLATES.python);
    setCurrentView("room");
  };

  // Leave Room
  const handleLeaveRoom = async () => {
    if (activeRoomId) {
      try {
        await fetch(`${apiBase}/api/code-rooms/${activeRoomId}/leave`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ participant_id: myUserId }),
        });
      } catch {}
    }
    setActiveRoomId(null);
    setRoomState(null);
    setCurrentView("lobby");
    fetchRoomsDirectory();
  };

  // Monaco Editor Mounted Callback
  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor;

    // Listen to cursor movement and broadcast to peers (throttled to 80ms)
    editor.onDidChangeCursorPosition((e: any) => {
      const now = Date.now();
      if (now - lastCursorSendRef.current > 80) {
        lastCursorSendRef.current = now;
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(
            JSON.stringify({
              type: "cursor_update",
              client_id: myClientId,
              cursor: {
                lineNumber: e.position.lineNumber,
                column: e.position.column,
              },
              sender_id: myUserId,
              sender_name: myName,
            })
          );
        }
      }
    });
  };

  // Code Change with Instant WebSocket Broadcast & Debounced HTTP Persistence
  const handleCodeChange = (newCode: string | undefined) => {
    if (isRemoteUpdatingRef.current) return;
    const val = newCode || "";
    setCode(val);
    setSyncStatus("saving");

    // 1. Send immediately over WebSocket for sub-10ms peer synchronization!
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: "code_change",
          client_id: myClientId,
          code: val,
          language,
          sender_id: myUserId,
          sender_name: myName,
        })
      );
      setSyncStatus("synced");
    }

    // 2. Debounce HTTP sync (600ms) as backup persistence
    if (debounceSyncRef.current) clearTimeout(debounceSyncRef.current);
    debounceSyncRef.current = setTimeout(async () => {
      if (activeRoomId) {
        try {
          await fetch(`${apiBase}/api/code-rooms/${activeRoomId}/sync-code`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              participant_id: myUserId,
              client_id: myClientId,
              code: val,
              language,
            }),
          });
        } catch {}
      }
      setSyncStatus("synced");
    }, 600);
  };

  // Switch Language Across Peers
  const handleLanguageChange = async (newLang: SupportedLang) => {
    setLanguage(newLang);
    const template = DEFAULT_TEMPLATES[newLang];
    setCode(template);
    setTerminalOutput(null);
    setRunSuccess(null);

    if (editorRef.current) {
      const editor = editorRef.current;
      const model = editor.getModel();
      if (model && model.getValue() !== template) {
        isRemoteUpdatingRef.current = true;
        editor.setValue(template);
        isRemoteUpdatingRef.current = false;
      }
    }

    // Broadcast over WebSocket immediately
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: "language_change",
          client_id: myClientId,
          language: newLang,
          code: template,
          sender_id: myUserId,
          sender_name: myName,
        })
      );
    }

    if (activeRoomId) {
      try {
        await fetch(`${apiBase}/api/code-rooms/${activeRoomId}/sync-code`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            participant_id: myUserId,
            client_id: myClientId,
            language: newLang,
            code: template,
          }),
        });
      } catch {}
    }
  };

  // Run Code Across All Peer Screens
  const handleRunCode = async () => {
    setIsRunning(true);
    setTerminalOutput(`Connecting to SkillBridge Execution Engine (Port 8000)...\nCompiling & executing ${language.toUpperCase()}...\n`);

    // Broadcast run event over WebSocket
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: "code_run",
          client_id: myClientId,
          language,
          code,
          sender_id: myUserId,
          sender_name: myName,
        })
      );
      return;
    }

    // HTTP fallback
    try {
      if (activeRoomId) {
        const res = await fetch(`${apiBase}/api/code-rooms/${activeRoomId}/run`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            participant_id: myUserId,
            name: myName,
            language,
            code,
          }),
        });
        if (res.ok) {
          const data: CodeRoomState = await res.json();
          setRoomState(data);
          setTerminalOutput(data.terminal_output || null);
          setRunSuccess(data.last_run_status === "success");
        }
      }
    } catch {
      setTerminalOutput("Error: Connection to Execution Engine timed out.");
      setRunSuccess(false);
    } finally {
      setIsRunning(false);
    }
  };

  // Send Team Chat message
  const handleSendChat = async () => {
    if (!chatInput.trim() || !activeRoomId || isSendingChat) return;
    const text = chatInput.trim();
    setChatInput("");
    setIsSendingChat(true);

    // Fast path: WebSocket
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: "chat_message",
          client_id: myClientId,
          text,
          sender_id: myUserId,
          sender_name: myName,
        })
      );
      setIsSendingChat(false);
      return;
    }

    // Fallback path: HTTP
    try {
      const res = await fetch(`${apiBase}/api/code-rooms/${activeRoomId}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          participant_id: myUserId,
          name: myName,
          text,
        }),
      });
      if (res.ok) {
        const data: CodeRoomState = await res.json();
        setRoomState(data);
      }
    } catch {} finally {
      setIsSendingChat(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleQuickJoin = () => {
    const target = roomsList.find((r) => r.can_join && r.participants_count > 0) || roomsList.find((r) => r.can_join);
    if (target) {
      handleJoinRoom(target.room_id);
    } else {
      handleJoinRoom("CODE001");
    }
  };

  // Active peer cursors within the last 15 seconds
  const activePeerCursors = useMemo(() => {
    const now = Date.now();
    return Object.entries(peerCursors).filter(
      ([id, c]) => id !== myClientId && id !== myUserId && now - c.timestamp < 15000
    );
  }, [peerCursors, myClientId, myUserId]);

  // ==========================================
  // VIEW 1: LOBBY
  // ==========================================
  if (currentView === "lobby") {
    return (
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {/* Header Bar */}
        <section className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-xl font-bold tracking-tight text-slate-900 sm:text-2xl">
                Collaborative Code Arena
              </h1>
              <p className="mt-1 text-sm text-slate-500">
                Real-time synchronized pair programming with instant multi-user typing, shared execution, and team discussion.
              </p>
              <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">
                <span className="font-semibold text-slate-400">Runtimes:</span>
                <span className="rounded-md bg-slate-100 px-2 py-0.5 font-mono text-[11px] font-bold text-slate-700">Python 3.12</span>
                <span className="rounded-md bg-slate-100 px-2 py-0.5 font-mono text-[11px] font-bold text-slate-700">Node.js 24</span>
                <span className="rounded-md bg-slate-100 px-2 py-0.5 font-mono text-[11px] font-bold text-slate-700">Java 21</span>
                <span className="rounded-md bg-slate-100 px-2 py-0.5 font-mono text-[11px] font-bold text-slate-700">C++ MinGW 15</span>
              </div>
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
                      sessionStorage.setItem("skillbridge_code_session_name", val);
                      localStorage.setItem("skillbridge_code_user_name", val);
                    }
                  }}
                  placeholder="Developer Name"
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
        <section className="mb-6 flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-xs sm:flex-row sm:items-center sm:justify-between">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search room code (e.g. CODE001, CODE042)..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setPage(1);
              }}
              className="w-full rounded-xl border border-slate-200 bg-slate-50 py-2.5 pl-10 pr-4 text-xs outline-none transition focus:border-indigo-500 focus:bg-white"
            />
          </div>

          <div className="flex flex-wrap items-center gap-1.5 text-xs font-semibold">
            {(["all", "active", "available"] as const).map((filter) => (
              <button
                key={filter}
                onClick={() => {
                  setStatusFilter(filter);
                  setPage(1);
                }}
                className={`rounded-lg px-3 py-1.5 capitalize transition ${
                  statusFilter === filter
                    ? "bg-slate-900 text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {filter === "all" ? "All Rooms" : filter === "active" ? "Active Coders" : "Available Seats"}
              </button>
            ))}
          </div>
        </section>

        {/* Rooms Grid */}
        <section className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {roomsList.map((room) => {
            const hasCoders = room.participants_count > 0;
            return (
              <div
                key={room.room_id}
                className="flex flex-col justify-between rounded-xl border border-slate-200 bg-white p-4 shadow-xs transition hover:border-slate-300"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-sm font-bold text-slate-900">
                      {room.room_id}
                    </span>
                    <span
                      className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-[11px] font-semibold ${
                        hasCoders ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-slate-100 text-slate-500"
                      }`}
                    >
                      <Users className="h-3 w-3" />
                      {room.participants_count} / {room.max_capacity}
                    </span>
                  </div>

                  <p className="mt-2 text-xs text-slate-500">
                    Collaborative Workspace
                  </p>

                  <div className="mt-3 flex items-center gap-2">
                    <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-mono font-bold uppercase text-slate-700">
                      {room.language}
                    </span>
                    <span className="text-[11px] text-slate-400">No time limit</span>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100">
                  <button
                    onClick={() => handleJoinRoom(room.room_id)}
                    className="w-full rounded-lg bg-slate-900 py-2 text-xs font-semibold text-white shadow-xs transition hover:bg-indigo-600"
                  >
                    Enter Workspace
                  </button>
                </div>
              </div>
            );
          })}
        </section>

        {/* Pagination Bar */}
        <div className="mt-6 flex items-center justify-between rounded-xl border border-slate-200 bg-white px-4 py-3 text-xs">
          <span className="text-slate-500">
            Page <span className="font-bold text-slate-900">{page}</span> of{" "}
            <span className="font-bold text-slate-900">{totalPages || 1}</span>
          </span>
          <div className="flex items-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="rounded-lg border border-slate-200 px-3 py-1.5 font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-40"
            >
              Previous
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              className="rounded-lg border border-slate-200 px-3 py-1.5 font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ==========================================
  // VIEW 2: COLLABORATIVE WORKSPACE (ROOM)
  // Shared Live Chat & Discussion Space
  // ==========================================
  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      {/* Top Workspace Header */}
      <div className="mb-5 flex flex-wrap items-center justify-between gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-xs">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-900 font-mono text-sm font-bold text-white">
            {activeRoomId}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-slate-900">Collaborative Workspace</h2>
              <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-semibold text-slate-600">
                No Time Limit
              </span>
              <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold border flex items-center gap-1 ${
                wsConnected ? "bg-emerald-50 text-emerald-700 border-emerald-200" : "bg-amber-50 text-amber-700 border-amber-200"
              }`}>
                <span className={`h-1.5 w-1.5 rounded-full ${wsConnected ? "bg-emerald-500 animate-pulse" : "bg-amber-400"}`} />
                {wsConnected ? "Real-Time Sync Active" : "Connecting..."}
              </span>
              <span className="rounded-full bg-slate-50 border border-slate-200 px-2 py-0.5 text-[10px] font-semibold text-slate-600">
                {roomState?.participants.length || 1} Connected
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Instant multi-user code synchronization & live execution across Port 8000
            </p>
          </div>
        </div>

        {/* Workspace Controls */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Language Selector */}
          <div className="flex items-center rounded-lg border border-slate-200 bg-slate-50 p-1">
            {(["python", "javascript", "java", "cpp"] as const).map((lang) => (
              <button
                key={lang}
                onClick={() => handleLanguageChange(lang)}
                className={`rounded-md px-2.5 py-1 text-xs font-semibold transition capitalize ${
                  language === lang
                    ? "bg-white text-slate-900 shadow-xs"
                    : "text-slate-500 hover:text-slate-900"
                }`}
              >
                {lang === "cpp" ? "C++" : lang === "javascript" ? "JS" : lang}
              </button>
            ))}
          </div>

          {/* Run Code Button */}
          <button
            onClick={handleRunCode}
            disabled={isRunning}
            className="inline-flex items-center gap-1.5 rounded-lg bg-slate-900 px-3.5 py-2 text-xs font-semibold text-white shadow-xs transition hover:bg-indigo-600 disabled:opacity-50"
          >
            <Play className={`h-3.5 w-3.5 fill-current ${isRunning ? "animate-spin" : ""}`} />
            {isRunning ? "Executing..." : "Run Code"}
          </button>

          {/* Leave Room Button */}
          <button
            onClick={handleLeaveRoom}
            className="inline-flex items-center gap-1 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition"
          >
            <LogOut className="h-3.5 w-3.5" /> Leave
          </button>
        </div>
      </div>

      {/* Main Workspace: Left Shared Live Chat Space, Right Editor & Terminal */}
      <div className="grid gap-5 lg:grid-cols-[360px_1fr]">
        {/* Left Column: Shared Live Chat Space & Connected Peers */}
        <div className="flex flex-col gap-4">
          {/* Active Collaborators */}
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-xs">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
                <Users className="h-3.5 w-3.5" />
                Connected Peers ({roomState?.participants.length || 1})
              </span>
              <span className="text-[10px] text-emerald-600 font-semibold flex items-center gap-1">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Live Sync
              </span>
            </div>

            <div className="mt-3 flex flex-wrap gap-1.5">
              {(roomState?.participants || [
                {
                  id: myUserId,
                  name: myName,
                  avatar: `https://api.dicebear.com/7.x/bottts/svg?seed=${myUserId}`,
                },
              ]).map((p) => {
                const isMe = p.id === myUserId;
                return (
                  <div
                    key={p.id}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-2 py-1 text-xs text-slate-700"
                  >
                    <img src={p.avatar} alt={p.name} className="h-4 w-4 rounded-full bg-slate-200" />
                    <span className="font-medium truncate max-w-[120px]">{p.name}</span>
                    {isMe && <span className="text-[10px] font-bold text-indigo-600">(You)</span>}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Shared Live Chat & Team Discussion Space */}
          <div className="flex flex-1 flex-col rounded-xl border border-slate-200 bg-white p-4 shadow-xs min-h-[480px]">
            <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-slate-700" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                  Shared Live Discussion
                </h3>
              </div>
              <span className="text-[11px] text-slate-400">
                {roomState?.messages.length || 0} messages
              </span>
            </div>

            {/* Chat Messages Feed */}
            <div className="mt-3 flex-1 overflow-y-auto space-y-2.5 max-h-[420px] pr-1">
              {(roomState?.messages || []).map((msg) => {
                const isSystem = msg.sender_id === "system";
                const isMe = msg.sender_id === myUserId;
                if (isSystem) {
                  return (
                    <div key={msg.id} className="rounded-lg bg-slate-50 p-2 text-[11px] text-slate-500 italic text-center border border-slate-100">
                      {msg.text}
                    </div>
                  );
                }
                return (
                  <div
                    key={msg.id}
                    className={`rounded-xl p-2.5 text-xs leading-relaxed ${
                      isMe
                        ? "bg-indigo-50 border border-indigo-100 text-indigo-950 ml-4"
                        : "bg-slate-50 border border-slate-100 text-slate-800 mr-4"
                    }`}
                  >
                    <div className="flex items-center justify-between font-semibold text-[11px]">
                      <span>{msg.sender_name}</span>
                      <span className="text-[9px] text-slate-400 font-normal">
                        {new Date(msg.timestamp * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                      </span>
                    </div>
                    <p className="mt-1 whitespace-pre-wrap">{msg.text}</p>
                  </div>
                );
              })}
              <div ref={chatBottomRef} />
            </div>

            {/* Chat Input */}
            <div className="mt-3 flex items-center gap-2 pt-3 border-t border-slate-100">
              <input
                type="text"
                placeholder="Share ideas, notes, or coordination..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSendChat()}
                className="flex-1 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs outline-none transition focus:border-indigo-500 focus:bg-white"
              />
              <button
                onClick={handleSendChat}
                disabled={!chatInput.trim() || isSendingChat}
                className="rounded-lg bg-slate-900 p-2 text-white transition hover:bg-indigo-600 disabled:opacity-40"
              >
                <Send className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Code Editor & Terminal */}
        <div className="flex flex-col gap-4">
          {/* Monaco Editor Container */}
          <div className="overflow-hidden rounded-xl border border-slate-200 bg-slate-900 shadow-xs">
            {/* Editor Sub-Header with Real-Time Peer Status */}
            <div className="flex flex-wrap items-center justify-between border-b border-slate-800 bg-slate-950 px-4 py-2 text-xs text-slate-300">
              <div className="flex items-center gap-2 flex-wrap">
                <FileCode className="h-3.5 w-3.5 text-indigo-400" />
                <span className="font-mono font-bold text-white uppercase text-[11px]">{language}</span>
                <span className="text-[11px] text-slate-500">
                  • solution.{language === "cpp" ? "cpp" : language === "javascript" ? "js" : language === "java" ? "java" : "py"}
                </span>

                {/* Real-Time Peer Activity Badges */}
                {lastPeerEdit && Date.now() - lastPeerEdit.timestamp < 4000 && (
                  <span className="inline-flex items-center gap-1 rounded bg-indigo-950/80 border border-indigo-700/60 px-2 py-0.5 text-[10px] font-bold text-indigo-300 animate-pulse">
                    <Zap className="h-2.5 w-2.5 text-indigo-400" />
                    Synced with {lastPeerEdit.name}
                  </span>
                )}

                {/* Active Peer Cursors */}
                {activePeerCursors.map(([id, peer]) => (
                  <span
                    key={id}
                    className="inline-flex items-center gap-1 rounded bg-slate-800 border border-slate-700 px-2 py-0.5 text-[10px] font-mono text-slate-300"
                  >
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    {peer.name}: Ln {peer.lineNumber}, Col {peer.column}
                  </span>
                ))}
              </div>

              <div className="flex items-center gap-2">
                <span
                  className={`text-[10px] font-medium ${
                    syncStatus === "saving" ? "text-amber-400 animate-pulse" : "text-emerald-400"
                  }`}
                >
                  {syncStatus === "saving" ? "Syncing..." : "● Real-Time"}
                </span>
                <button
                  onClick={handleCopy}
                  className="inline-flex items-center gap-1 rounded bg-slate-800 px-2 py-0.5 text-[10px] font-semibold text-slate-300 hover:bg-slate-700"
                >
                  {copied ? <Check className="h-3 w-3 text-emerald-400" /> : <Copy className="h-3 w-3" />}
                  {copied ? "Copied" : "Copy"}
                </button>
                <button
                  onClick={() => handleLanguageChange(language)}
                  className="inline-flex items-center gap-1 rounded bg-slate-800 px-2 py-0.5 text-[10px] font-semibold text-slate-300 hover:bg-slate-700"
                >
                  <RotateCcw className="h-3 w-3" /> Reset
                </button>
              </div>
            </div>

            {/* Monaco Editor Component with onMount and Real-Time Sync */}
            <div className="p-1">
              <MonacoEditor
                height="450px"
                language={language}
                theme="vs-dark"
                value={code}
                onChange={handleCodeChange}
                onMount={handleEditorDidMount}
                options={{
                  minimap: { enabled: false },
                  fontSize: 13,
                  lineNumbers: "on",
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  tabSize: 4,
                  wordWrap: "on",
                }}
              />
            </div>
          </div>

          {/* Terminal Output */}
          <div className="overflow-hidden rounded-xl border border-slate-200 bg-slate-950 shadow-xs">
            <div className="flex items-center justify-between border-b border-slate-800 bg-slate-900 px-4 py-2 text-xs">
              <div className="flex items-center gap-2">
                <Terminal className="h-3.5 w-3.5 text-emerald-400" />
                <span className="font-mono font-bold text-white text-[11px]">Execution Output</span>
                {runSuccess !== null && (
                  <span
                    className={`inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[10px] font-bold ${
                      runSuccess ? "bg-emerald-500/20 text-emerald-300" : "bg-red-500/20 text-red-300"
                    }`}
                  >
                    {runSuccess ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
                    {runSuccess ? "STATUS 0 (SUCCESS)" : "STATUS 1 (FAILED)"}
                  </span>
                )}
              </div>
              <button
                onClick={() => setTerminalOutput(null)}
                className="text-[11px] text-slate-400 hover:text-white"
              >
                Clear
              </button>
            </div>

            <pre className="p-4 font-mono text-xs leading-relaxed text-slate-200 max-h-56 overflow-y-auto whitespace-pre-wrap">
              {terminalOutput || "Click 'Run Code' above to compile and execute across all peer screens (Port 8000)..."}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
