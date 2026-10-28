"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Trophy,
  Clock,
  CheckCircle2,
  XCircle,
  ArrowRight,
  RotateCcw,
  Sparkles,
  Award,
  BookOpen,
  BrainCircuit,
  Zap,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

import APTITUDE_100_POOL from "../data/aptitude_pool.json";

export type Question = {
  id: string;
  category: string;
  difficulty: string;
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
};

interface AptitudeArenaProps {
  apiBase: string;
}

// Helper to shuffle and pick N questions
function pickRandomQuestions(pool: Question[], count: number = 15): Question[] {
  const shuffled = [...pool].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
}

export default function AptitudeArena({ apiBase }: AptitudeArenaProps) {
  const [questions, setQuestions] = useState<Question[]>(() =>
    pickRandomQuestions(APTITUDE_100_POOL as Question[], 15)
  );
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [isAnswered, setIsAnswered] = useState(false);
  const [score, setScore] = useState(0);
  const [timeLeft, setTimeLeft] = useState(45);
  const [gameState, setGameState] = useState<"intro" | "playing" | "summary">("intro");
  const [answersLog, setAnswersLog] = useState<
    { question: Question; isCorrect: boolean; selected: number }[]
  >([]);
  const [showReview, setShowReview] = useState(false);

  // Function to load a fresh set of 15 questions
  const loadFreshQuiz = useCallback(async () => {
    try {
      const res = await fetch(`${apiBase}/api/aptitude-questions?count=15&shuffle=true`);
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data.questions) && data.questions.length > 0) {
          setQuestions(data.questions);
          return;
        }
      }
    } catch {
      // Fallback to client-side shuffle from 100 questions
    }
    setQuestions(pickRandomQuestions(APTITUDE_100_POOL as Question[], 15));
  }, [apiBase]);

  // Load fresh 15 on component mount
  useEffect(() => {
    loadFreshQuiz();
  }, [loadFreshQuiz]);

  // Timer countdown
  useEffect(() => {
    if (gameState !== "playing" || isAnswered) return;

    if (timeLeft <= 0) {
      handleTimeOut();
      return;
    }

    const timer = setInterval(() => {
      setTimeLeft((prev) => prev - 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [gameState, timeLeft, isAnswered]);

  const handleStartGame = async () => {
    await loadFreshQuiz();
    setGameState("playing");
    setCurrentIndex(0);
    setScore(0);
    setSelectedOption(null);
    setIsAnswered(false);
    setTimeLeft(45);
    setAnswersLog([]);
    setShowReview(false);
  };

  const handleSelectOption = (idx: number) => {
    if (isAnswered) return;
    setSelectedOption(idx);
    setIsAnswered(true);

    const currentQ = questions[currentIndex];
    const isCorrect = idx === currentQ.correctIndex;
    const speedBonus = Math.max(0, Math.round(timeLeft * 1.5));
    const pointsEarned = isCorrect ? 100 + speedBonus : 0;

    if (isCorrect) {
      setScore((prev) => prev + pointsEarned);
    }

    setAnswersLog((prev) => [
      ...prev,
      { question: currentQ, isCorrect, selected: idx },
    ]);
  };

  const handleTimeOut = () => {
    const currentQ = questions[currentIndex];
    setIsAnswered(true);
    setSelectedOption(-1);
    setAnswersLog((prev) => [
      ...prev,
      { question: currentQ, isCorrect: false, selected: -1 },
    ]);
  };

  const handleNext = () => {
    if (currentIndex + 1 < questions.length) {
      setCurrentIndex((prev) => prev + 1);
      setSelectedOption(null);
      setIsAnswered(false);
      setTimeLeft(45);
    } else {
      setGameState("summary");
    }
  };

  const currentQ = questions[currentIndex] || (APTITUDE_100_POOL[0] as Question);
  const correctCount = answersLog.filter((a) => a.isCorrect).length;
  const totalCount = questions.length;
  const accuracy = totalCount > 0 ? Math.round((correctCount / totalCount) * 100) : 0;

  if (gameState === "intro") {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 shadow-xs">
          <div className="border-b border-slate-100 pb-5">
            <h1 className="text-xl font-bold tracking-tight text-slate-900 sm:text-2xl">
              Aptitude & Technical Assessment
            </h1>
            <p className="mt-2 text-sm leading-relaxed text-slate-600">
              Evaluates quantitative reasoning, logical problem solving, and verbal comprehension with timed questions and verified step-by-step explanations.
            </p>
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Test Length</span>
              <div className="mt-1.5 text-base font-bold text-slate-900">15 Questions</div>
              <p className="mt-1 text-xs text-slate-500">Timed adaptive assessment</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Time Per Question</span>
              <div className="mt-1.5 text-base font-bold text-slate-900">45 Seconds</div>
              <p className="mt-1 text-xs text-slate-500">Calculates speed & accuracy</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Feedback</span>
              <div className="mt-1.5 text-base font-bold text-slate-900">Step-by-Step</div>
              <p className="mt-1 text-xs text-slate-500">Complete logic rationale</p>
            </div>
          </div>

          <div className="mt-8 flex items-center justify-between border-t border-slate-100 pt-5">
            <span className="text-xs text-slate-500">
              Ready to begin when you are. Answers are calibrated automatically.
            </span>
            <button
              onClick={handleStartGame}
              className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-5 py-2.5 text-xs font-bold text-white shadow-xs transition hover:bg-indigo-600"
            >
              Start Assessment <ArrowRight className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (gameState === "summary") {
    return (
      <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6">
        <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
          <div className="text-center">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600">
              <Trophy className="h-8 w-8" />
            </div>
            <h2 className="mt-4 text-2xl font-bold text-slate-950">Test Completed!</h2>
            <p className="mt-1 text-sm text-slate-500">
              Finished 15 randomized screening questions from the 100-question pool.
            </p>
          </div>

          <div className="mt-8 grid grid-cols-3 gap-3 text-center">
            <div className="rounded-xl bg-slate-50 p-4">
              <div className="text-xs font-semibold uppercase text-slate-400">Total Score</div>
              <div className="mt-1 text-2xl font-bold text-indigo-600">{score}</div>
            </div>
            <div className="rounded-xl bg-slate-50 p-4">
              <div className="text-xs font-semibold uppercase text-slate-400">Correct Answers</div>
              <div className="mt-1 text-2xl font-bold text-emerald-600">
                {correctCount} / {totalCount}
              </div>
            </div>
            <div className="rounded-xl bg-slate-50 p-4">
              <div className="text-xs font-semibold uppercase text-slate-400">Accuracy</div>
              <div className="mt-1 text-2xl font-bold text-slate-900">{accuracy}%</div>
            </div>
          </div>

          {/* Action buttons */}
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <button
              onClick={handleStartGame}
              className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl bg-emerald-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700"
            >
              <RotateCcw className="h-4 w-4" /> Retake Test (New 15 Questions)
            </button>
            <button
              onClick={() => setShowReview(!showReview)}
              className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-slate-300"
            >
              {showReview ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              {showReview ? "Hide Details" : "Review All 15 Questions"}
            </button>
          </div>

          {/* Question Review Section */}
          {showReview && (
            <div className="mt-8 border-t border-slate-100 pt-6">
              <h3 className="text-base font-bold text-slate-900 mb-4">
                Detailed Solutions & Explanations (15 Questions)
              </h3>
              <div className="grid gap-4">
                {answersLog.map((log, i) => (
                  <div
                    key={i}
                    className={`rounded-xl border p-4 text-left ${
                      log.isCorrect
                        ? "border-emerald-200 bg-emerald-50/40"
                        : "border-red-200 bg-red-50/40"
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <span className="text-xs font-bold uppercase text-slate-500">
                          Q{i + 1} • {log.question.category} ({log.question.difficulty})
                        </span>
                        <h4 className="mt-1 text-sm font-semibold text-slate-900">
                          {log.question.question}
                        </h4>
                      </div>
                      <span
                        className={`inline-flex shrink-0 items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-bold ${
                          log.isCorrect
                            ? "bg-emerald-100 text-emerald-800"
                            : "bg-red-100 text-red-800"
                        }`}
                      >
                        {log.isCorrect ? (
                          <>
                            <CheckCircle2 className="h-3 w-3" /> Correct
                          </>
                        ) : (
                          <>
                            <XCircle className="h-3 w-3" /> Incorrect
                          </>
                        )}
                      </span>
                    </div>

                    <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-xs">
                      {log.question.options.map((opt, optIdx) => {
                        const isCorrectOpt = optIdx === log.question.correctIndex;
                        const wasChosen = optIdx === log.selected;
                        let itemClass = "bg-white/80 border-slate-200 text-slate-700";
                        if (isCorrectOpt) itemClass = "bg-emerald-100 border-emerald-300 text-emerald-900 font-semibold";
                        else if (wasChosen) itemClass = "bg-red-100 border-red-300 text-red-900";

                        return (
                          <div
                            key={optIdx}
                            className={`rounded-lg border px-2.5 py-1.5 ${itemClass}`}
                          >
                            <span className="font-bold mr-1.5">{String.fromCharCode(65 + optIdx)}.</span>
                            {opt}
                            {isCorrectOpt && " ✓"}
                            {wasChosen && !isCorrectOpt && " (Your answer)"}
                          </div>
                        );
                      })}
                    </div>

                    <div className="mt-3 rounded-lg bg-white/90 p-2.5 text-xs text-slate-600 border border-slate-100">
                      <span className="font-bold text-slate-800">Explanation: </span>
                      {log.question.explanation}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
      {/* Header bar */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-700 shadow-sm">
            <BookOpen className="h-3.5 w-3.5 text-emerald-600" />
            {currentQ.category}
          </span>
          <span className="ml-2 text-xs font-semibold text-slate-600">
            Question {currentIndex + 1} of {totalCount}
          </span>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 text-sm font-bold text-slate-900">
            <Zap className="h-4 w-4 text-amber-500" />
            {score} pts
          </div>
          <div
            className={`flex items-center gap-1 rounded-lg px-2.5 py-1 text-sm font-bold ${
              timeLeft <= 10
                ? "bg-red-50 text-red-600 animate-pulse"
                : "bg-emerald-50 text-emerald-700"
            }`}
          >
            <Clock className="h-4 w-4" />
            {timeLeft}s
          </div>
        </div>
      </div>

      {/* Timer Bar */}
      <div className="mb-6 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
        <div
          className={`h-full transition-all duration-1000 ${
            timeLeft <= 10 ? "bg-red-500" : "bg-emerald-600"
          }`}
          style={{ width: `${(timeLeft / 45) * 100}%` }}
        />
      </div>

      {/* Question Card */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
        <div className="mb-2 text-xs font-bold uppercase tracking-wider text-slate-400">
          Difficulty: {currentQ.difficulty}
        </div>
        <h2 className="text-lg font-semibold leading-relaxed text-slate-950 sm:text-xl">
          {currentQ.question}
        </h2>

        {/* Options */}
        <div className="mt-6 grid gap-3">
          {currentQ.options.map((opt, idx) => {
            const isSelected = selectedOption === idx;
            const isCorrect = idx === currentQ.correctIndex;
            let btnStyle = "border-slate-200 hover:border-emerald-300 hover:bg-slate-50";

            if (isAnswered) {
              if (isCorrect) {
                btnStyle = "border-emerald-500 bg-emerald-50 text-emerald-950 font-semibold";
              } else if (isSelected) {
                btnStyle = "border-red-500 bg-red-50 text-red-950 font-semibold";
              } else {
                btnStyle = "border-slate-100 opacity-50";
              }
            }

            return (
              <button
                key={idx}
                disabled={isAnswered}
                onClick={() => handleSelectOption(idx)}
                className={`flex w-full items-center justify-between rounded-xl border p-4 text-left text-sm transition sm:text-base ${btnStyle}`}
              >
                <div className="flex items-center gap-3">
                  <span className="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200 bg-white text-xs font-bold text-slate-600">
                    {String.fromCharCode(65 + idx)}
                  </span>
                  <span>{opt}</span>
                </div>
                {isAnswered && isCorrect && <CheckCircle2 className="h-5 w-5 text-emerald-600" />}
                {isAnswered && isSelected && !isCorrect && (
                  <XCircle className="h-5 w-5 text-red-600" />
                )}
              </button>
            );
          })}
        </div>

        {/* Explanation & Next Button */}
        {isAnswered && (
          <div className="mt-6 border-t border-slate-100 pt-5">
            <div className="rounded-xl bg-slate-50 p-4">
              <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-slate-500">
                <Sparkles className="h-3.5 w-3.5 text-emerald-600" />
                Step-by-Step Explanation
              </div>
              <p className="mt-1 text-sm text-slate-700">{currentQ.explanation}</p>
            </div>

            <div className="mt-5 flex justify-end">
              <button
                onClick={handleNext}
                className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-6 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700"
              >
                {currentIndex + 1 < questions.length ? "Next Question" : "View Results"}
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
