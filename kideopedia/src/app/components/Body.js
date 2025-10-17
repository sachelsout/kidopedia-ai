"use client";

import { useState } from "react";
import { Input, Button } from "@chakra-ui/react";
import { Baloo_2 } from "next/font/google";

const baloo = Baloo_2({
  subsets: ["latin"],
  weight: ["700"],
});

export default function Body() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  // 🔹 Function to call Flask backend
  const handleAsk = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setAnswer("");

    try {
      const res = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setAnswer(data.answer || "No answer received.");
    } catch (err) {
      console.error("Error:", err);
      setAnswer("Error: could not reach the backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-[#5b78b4] text-center">
      {/* Panda Mascot */}
      <div className="panda-container">
        <svg
          width="120"
          height="120"
          viewBox="0 0 200 200"
          xmlns="http://www.w3.org/2000/svg"
          className="panda"
        >
          <circle cx="100" cy="100" r="90" fill="white" />
          <circle cx="60" cy="80" r="25" fill="#a9e5c1" />
          <circle cx="140" cy="80" r="25" fill="#a9e5c1" />
          <circle cx="70" cy="100" r="15" fill="black" />
          <circle cx="130" cy="100" r="15" fill="black" />
          <circle cx="75" cy="95" r="5" fill="white" />
          <circle cx="135" cy="95" r="5" fill="white" />
          <ellipse cx="100" cy="135" rx="25" ry="15" fill="#a9e5c1" />
        </svg>
      </div>

      {/* Kidopedia Title */}
      <label
        className={`field ${baloo.className}`}
        style={{
          fontWeight: "700",
          fontSize: "3.4rem",
          color: "white",
          position: "relative",
          letterSpacing: "1px",
          marginBottom: "3.5rem",
        }}
      >
        <span className="kidopedia">
          K
          <span className="i-wrap">
            <span className="i-letter">i</span>
            <span className="i-dot" />
          </span>
          doped
          <span className="i-wrap">
            <span className="i-letter">i</span>
            <span className="i-dot" />
          </span>
          a
        </span>
      </label>

      {/* Input and Button */}
      <div className="action-wrapper">
        <Input
          size="md"
          placeholder="Ask me anything"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="center-input"
          style={{
            width: "200px",
            textAlign: "center",
            borderRadius: "50px",
          }}
        />
        <Button
          size="md"
          colorPalette="green"
          className="center-button"
          onClick={handleAsk}
          disabled={loading}
        >
          {loading ? "Thinking..." : "Ask"}
        </Button>

        {/* Answer display */}
        {answer && (
          <p style={{ color: "white", marginTop: "1rem", width: "70%" }}>
            <strong>Answer:</strong> {answer}
          </p>
        )}
      </div>

      {/* existing styles remain unchanged */}
      <style jsx>{`
        main {
          height: 100vh;
          width: 100%;
          margin: 0;
          padding: 0;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          background-color: #5b78b4;
          overflow: hidden;
          position: fixed;
          top: 0;
          left: 0;
        }
        .panda-container {
          display: flex;
          justify-content: center;
          align-items: center;
          margin-bottom: -20px;
          margin-top: -20px;
          animation: bounce 3s ease-in-out infinite;
        }

        .panda {
          width: 160px;
          height: 160px;
        }

        @keyframes bounce {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-10px);
          }
        }

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

        @keyframes iPulse {
          0%, 100% { transform: translate(-50%, 0) scale(1); opacity: 1; }
          50% { transform: translate(-50%, 0) scale(1.18); opacity: 0.9; }
        }

        .action-wrapper {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 1.2rem;
          margin-top: 0.25rem;
          width: 100%;
        }

        .center-button {
          width: 200px;
          border-radius: 50px;
          box-shadow: 3px 6px 0px rgba(0, 0, 0, 0.3);
          transition: all 0.25s ease-in-out;
        }

        :global(.center-button:hover) {
          background-color: #48bb78 !important;
          transform: translateY(-3px) scale(1.05);
          box-shadow: 0 0 25px rgba(72, 187, 120, 0.9), 0 0 50px rgba(72, 187, 120, 0.6);
          transition: all 0.25s ease-in-out;
        }

        @media (max-width: 600px) {
          .i-dot {
            top: -0.55em;
            width: 0.25em;
            height: 0.25em;
          }
        }
      `}</style>
    </main>
  );
}
