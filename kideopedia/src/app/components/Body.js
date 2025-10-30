// Body.js
"use client";

import { useState } from "react";
import { Input, Button, Image } from "@chakra-ui/react";
import { Baloo_2 } from "next/font/google";

const baloo = Baloo_2({ subsets: ["latin"], weight: ["700"] });

export default function Body() {
  // --- UI / conversation state ---
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [sessionId] = useState("local_user"); // fixed session id (can be dynamic later)
  // separate loading states
  const [isTextLoading, setIsTextLoading] = useState(false);
  const [isImageLoading, setIsImageLoading] = useState(false);

  // --- helper to detect if the user is asking for an image ---
  const detectImageRequest = (text = "") => {
    const keywords = [
      "draw",
      "picture",
      "image",
      "illustrate",
      "show me",
      "paint",
      "generate image",
      "make an image",
      "make a picture",
      "create an image",
      "sketch",
      "design",
    ];
    const lowered = text.toLowerCase();
    return keywords.some((kw) => lowered.includes(kw));
  };

  // --- Ask question (text or image) ---
  const handleAsk = async () => {
    if (!question.trim()) return;

    // determine request type
    const isImageRequest = detectImageRequest(question);
    // set appropriate loader
    setAnswer("");
    setImageUrl("");
    if (isImageRequest) {
      setIsImageLoading(true);
      setIsTextLoading(false);
    } else {
      setIsTextLoading(true);
      setIsImageLoading(false);
    }

    const currentQuestion = question;
    setQuestion(""); // clear input

    const endpoint = "http://localhost:8002/api/chat";

    try {
      const payload = {
        message: currentQuestion,
        session_id: sessionId,
        is_image_request: isImageRequest,
        last_image_url: imageUrl || null,
      };

      console.log("📤 Sending to backend:", payload);

      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const text = await res.text().catch(() => "");
        throw new Error(`Network error: ${res.status} ${res.statusText} ${text}`);
      }

      const data = await res.json();
      console.log("📥 Received from backend:", data);

      if (data.reply) setAnswer(data.reply);
      if (data.image_url) setImageUrl(data.image_url);
    } catch (err) {
      console.error("Error:", err);
      setAnswer("Error: could not reach the backend.");
    } finally {
      setIsTextLoading(false);
      setIsImageLoading(false);
    }
  };

  // --- Reset conversation ---
  const handleReset = async () => {
    if (!window.confirm("Start a new chat? Your previous conversation will be lost.")) return;

    setIsTextLoading(true);
    setIsImageLoading(false);
    setAnswer("");
    setImageUrl("");
    setQuestion("");

    try {
      const resetEndpoint = `http://localhost:8002/api/reset`;
      await fetch(resetEndpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });
    } catch (err) {
      console.error("Error resetting conversation:", err);
      setAnswer("Error: could not reset conversation.");
    } finally {
      setIsTextLoading(false);
    }
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-[#5b78b4] text-center">
      {/* Panda Mascot */}
      <div className="panda-container">
        <svg
          width="160"
          height="160"
          viewBox="0 0 200 200"
          xmlns="http://www.w3.org/2000/svg"
          className={`panda ${isTextLoading ? "typing" : ""} ${isImageLoading ? "drawing" : ""}`}
        >
          {/* face */}
          <circle cx="100" cy="100" r="90" fill="white" />
          {/* ears */}
          <ellipse cx="50" cy="50" rx="28" ry="28" fill="#2b2b2b" />
          <ellipse cx="150" cy="50" rx="28" ry="28" fill="#2b2b2b" />
          {/* eye patches */}
          <ellipse cx="70" cy="85" rx="28" ry="22" fill="#2b2b2b" />
          <ellipse cx="130" cy="85" rx="28" ry="22" fill="#2b2b2b" />
          {/* eyes */}
          <circle cx="70" cy="85" r="8" fill="#fff" />
          <circle cx="130" cy="85" r="8" fill="#fff" />
          {/* nose/mouth */}
          <ellipse cx="100" cy="125" rx="22" ry="12" fill="#a9e5c1" />
          {/* small brush (only visible when drawing - controlled in CSS) */}
          <g className="brush" transform="translate(88,125)">
            <rect x="18" y="12" width="36" height="6" rx="3" ry="3" fill="#6b4226" />
            <rect x="50" y="8" width="6" height="18" rx="3" ry="3" fill="#6b4226" transform="rotate(20 53 17)"/>
            <ellipse cx="60" cy="6" rx="10" ry="6" fill="#e84c3d" className="brush-tip" />
          </g>
          {/* pencil lines / strokes (appear while drawing) */}
          <g className="ink-strokes" transform="translate(-10,-10)">
            <path d="M120 170 q20 -30 60 -30" stroke="#e84c3d" strokeWidth="3" fill="none" strokeLinecap="round" />
            <path d="M110 160 q10 -20 45 -20" stroke="#f6b93b" strokeWidth="3" fill="none" strokeLinecap="round" />
          </g>
        </svg>
      </div>

      {/* Kidopedia Title */}
      <label
        className={`${baloo.className} field`}
        style={{
          fontWeight: "700",
          fontSize: "3.4rem",
          color: "white",
          position: "relative",
          letterSpacing: "1px",
          marginBottom: "2.5rem",
        }}
      >
        <span className="kidopedia">
          K
          <span className="i-wrap">
            <span className="i-letter">i</span>
            <span className="i-dot" />
          </span>
          d
          <span className="i-letter">o</span>
          p
          <span className="i-letter">e</span>
          d
          <span className="i-wrap">
            <span className="i-letter">i</span>
            <span className="i-dot" />
          </span>
          a<span style={{ marginRight: "0.01em" }}> </span>
<span className="i-wrap">
  <span className="i-letter">AI</span>
  <span className="i-dot ai-dot" />
</span>

        </span>
      </label>

      {/* Input and Buttons */}
      <div className="action-wrapper">
        <Input
          size="md"
          placeholder="Ask me anything"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="center-input"
          style={{ width: "220px", textAlign: "center", borderRadius: "50px" }}
        />

        <Button
          size="lg"
          colorPalette="green"
          className="center-button"
          onClick={handleAsk}
          disabled={isTextLoading || isImageLoading}
        >
          {(isTextLoading && "Thinking...") || (isImageLoading && "Creating your image...") || "Ask"}
        </Button>

        <Button size="sm" colorScheme="red" mt={2} onClick={handleReset} disabled={isTextLoading || isImageLoading}>
          New Chat
        </Button>

        {/* Loading paws / animation area */}
        <div className="panda-spinner">
          {/* Typing animation: show small dots when text loading */}
          {isTextLoading && (
            <div className="typing-dots" aria-hidden>
              <span></span>
              <span></span>
              <span></span>
            </div>
          )}

          {/* Drawing animation: show small brush movement when image loading */}
          {isImageLoading && (
            <div className="drawing-anim" aria-hidden>
              <div className="paint-swoosh"></div>
            </div>
          )}
        </div>

        {/* Answer display */}
        {!isTextLoading && answer && (
          <p style={{ color: "white", marginTop: "1rem", width: "70%" }}>
            <strong>Answer:</strong> {answer}
          </p>
        )}

        {/* Image display */}
        {imageUrl ? (
          <div style={{ marginTop: "1.5rem" }}>
            <p style={{ color: "white", marginBottom: "0.5rem" }}>
              <strong>AI Generated Image:</strong>
            </p>
            <Image
              src={imageUrl}
              alt="AI generated response"
              borderRadius="16px"
              width="100%"
              maxWidth="450px"
              objectFit="contain"
              className="fade-in-image hover-glow"
              onClick={() => window.open(imageUrl, "_blank")}
              style={{
                border: "6px solid #C7F2E3",
                backgroundColor: "#F9FFF9",
                padding: "8px",
                cursor: "pointer",
                marginBottom: "4px",
              }}
            />
          </div>
        ) : null}
      </div>

      {/* Styles */}
      <style jsx>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        main {
          min-height: 100vh;
          width: 100%;
          padding: 6rem 1rem; /* increased vertical padding to prevent cutoff */
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: flex-start; /* keeps layout from stretching oddly */
          background-color: #5b78b4;
          overflow-y: auto; /* allow scrolling if needed */
        }
        .panda-container {
          display: flex;
          justify-content: center;
          align-items: center;
          margin-top: 1.5rem;
          margin-bottom: 1rem;
          animation: bounce 3s ease-in-out infinite;
        }
        @keyframes bounce {
          0%,
          100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-8px);
          }
        }

        /* Panda idle -> typing -> drawing styles */
        .panda {
          width: 160px;
          height: 160px;
          transition: transform 0.25s ease;
        }
        /* subtle head-tilt while typing */
        .panda.typing {
          transform: translateY(-4px) rotate(-2deg);
        }
        /* while drawing, make the brush visible and animate it */
        .panda.drawing .brush {
          opacity: 1;
          transform-origin: 40px 10px;
          animation: brushStroke 1s infinite linear;
        }
        .panda .brush {
          opacity: 0;
          transition: opacity 0.2s ease;
        }
        .panda .brush-tip {
          filter: drop-shadow(0 2px 2px rgba(0, 0, 0, 0.15));
        }
        .panda .ink-strokes {
          opacity: 0;
          transition: opacity 0.2s ease;
        }
        .panda.drawing .ink-strokes {
          opacity: 1;
          animation: inkFlow 1.2s infinite ease-in-out;
        }
        @keyframes brushStroke {
          0% {
            transform: rotate(-20deg) translateY(0);
          }
          50% {
            transform: rotate(10deg) translateY(-4px);
          }
          100% {
            transform: rotate(-20deg) translateY(0);
          }
        }
        @keyframes inkFlow {
          0% {
            transform: translateX(0);
            opacity: 0.8;
          }
          50% {
            transform: translateX(2px);
            opacity: 1;
          }
          100% {
            transform: translateX(0);
            opacity: 0.8;
          }
        }

        .action-wrapper {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 1rem;
          margin-top: 0.5rem;
          width: 100%;
        }

        .center-button {
          width: 220px;
          border-radius: 50px;
          box-shadow: 3px 6px 0px rgba(0, 0, 0, 0.3);
          transition: all 0.3s ease-in-out;
          animation: pulseGlow 3s ease-in-out infinite;
        }
        :global(.center-button:hover) {
          transform: translateY(-3px) scale(1.03);
          box-shadow: 0 0 25px rgba(56, 161, 105, 0.6), 0 0 40px rgba(56, 161, 105, 0.4);
        }
        @keyframes pulseGlow {
          0% {
            box-shadow: 0 0 10px rgba(56, 161, 105, 0.4), 0 0 20px rgba(56, 161, 105, 0.2);
          }
          50% {
            box-shadow: 0 0 20px rgba(56, 161, 105, 0.8), 0 0 35px rgba(56, 161, 105, 0.5);
          }
          100% {
            box-shadow: 0 0 10px rgba(56, 161, 105, 0.4), 0 0 20px rgba(56, 161, 105, 0.2);
          }
        }

        .typing-dots {
          display: flex;
          gap: 8px;
          margin-top: 12px;
        }
        .typing-dots span {
          width: 10px;
          height: 10px;
          background: #fff;
          border-radius: 50%;
          opacity: 0.6;
          animation: jump 1s infinite ease-in-out;
        }
        .typing-dots span:nth-child(2) {
          animation-delay: 0.15s;
        }
        .typing-dots span:nth-child(3) {
          animation-delay: 0.3s;
        }
        @keyframes jump {
          0%,
          80%,
          100% {
            transform: translateY(0);
            opacity: 0.6;
          }
          40% {
            transform: translateY(-8px);
            opacity: 1;
          }
        }

        .drawing-anim {
          margin-top: 12px;
          width: 140px;
          height: 18px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .paint-swoosh {
          width: 60px;
          height: 6px;
          border-radius: 999px;
          background: linear-gradient(90deg, #f6b93b, #e84c3d);
          transform-origin: left center;
          animation: swoosh 1s infinite linear;
          box-shadow: 0 4px 10px rgba(0, 0, 0, 0.12);
        }
        @keyframes swoosh {
          0% {
            transform: scaleX(0.2) translateX(-10px);
            opacity: 0.6;
          }
          50% {
            transform: scaleX(1) translateX(6px);
            opacity: 1;
          }
          100% {
            transform: scaleX(0.2) translateX(-10px);
            opacity: 0.6;
          }
        }

        .fade-in-image {
          animation: fadeIn 0.9s ease-in-out;
          border-radius: 16px;
          transition: transform 0.25s ease, box-shadow 0.25s ease;
          box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25); /* base shadow moved from inline */
        }
        :global(.hover-glow) {
          transition: transform 0.25s ease, box-shadow 0.25s ease;
          will-change: transform, box-shadow;
        }
        :global(.hover-glow:hover) {
          transform: scale(1.03);
          box-shadow: 0 0 25px rgba(56, 161, 105, 0.9), 0 0 40px rgba(56, 161, 105, 0.5) !important;
        }
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(6px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        /* i dot animation for title */
        .i-wrap {
          position: relative;
          display: inline-block;
        }
        .i-letter {
          color: white;
          position: relative;
          z-index: 1;
        }
        .i-dot {
          position: absolute;
          left: 50%;
          top: 0.22em;
          width: 0.28em;
          height: 0.28em;
          border-radius: 50%;
          background: #38a169;
          transform: translate(-50%, 0);
          z-index: 5;
          pointer-events: none;
          animation: iPulse 3s ease-in-out infinite;
        }
        .i-dot.ai-dot {
          top: 0.1em;
          left: 81%;         /* align more naturally with the uppercase I */
          width: 0.26em;
          height: 0.26em;
        }
        @keyframes iPulse {
          0%,
          100% {
            transform: translate(-50%, 0) scale(1);
            opacity: 1;
          }
          50% {
            transform: translate(-50%, 0) scale(1.12);
            opacity: 0.92;
          }
        }

        @media (max-width: 600px) {
          .i-dot {
            top: -0.55em;
            width: 0.25em;
            height: 0.25em;
          }
          .center-button {
            width: 180px;
          }
        }
      `}</style>
    </main>
  );
}
