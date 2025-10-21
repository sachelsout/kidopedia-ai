"use client";

import { useState } from "react";
import { Input, Button, Image } from "@chakra-ui/react";
import { Baloo_2 } from "next/font/google";

const baloo = Baloo_2({
  subsets: ["latin"],
  weight: ["700"],
});

export default function Body() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [loading, setLoading] = useState(false);

  // 🔹 Function to call Flask backend
  const handleAsk = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setAnswer("");
    setImageUrl("");
    setQuestion(""); // clear input field after click

    try {
      const res = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setAnswer(data.answer || "No answer received.");
      setImageUrl(data.image_url || "");
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
          size="lg"
          colorPalette="green"
          className="center-button"
          onClick={handleAsk}
          disabled={loading}
        >
          {loading ? "Thinking..." : "Ask"}
        </Button>

        {/* Answer display */}
        {loading ? (
          <div className="panda-spinner">
            <div className="paw paw1"></div>
            <div className="paw paw2"></div>
            <div className="paw paw3"></div>
            <div className="paw paw4"></div>
          </div>
        ) : (
          answer && (
            <p style={{ color: 'white', marginTop: '1rem', width: '70%' }}>
              <strong>Answer:</strong> {answer}
            </p>
          )
        )}
        {imageUrl && (
          <div style={{ marginTop: "1.5rem" }}>
            <Image
              src={imageUrl}
              alt="Answer related"
              borderRadius="16px"
              width="100%"
              height="65%"
              maxWidth="450px"
              objectFit="contain"
              className="fade-in-image"
              style={{
                border: '6px solid #C7F2E3',
                backgroundColor: '#F9FFF9',
                padding: '8px',
                // Adaptive dual-layer shadow: dark and pastel, with soft gradient
                boxShadow:
                  '0 6px 20px rgba(0, 0, 0, 0.25), 0 0 15px rgba(199, 242, 227, 0.6)',
                transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                cursor: 'pointer',
                marginBottom: '4px'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'scale(1.05)';
                e.currentTarget.style.boxShadow =
                  '0 12px 30px rgba(0, 0, 0, 0.35), 0 0 25px rgba(199, 242, 227, 0.9)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'scale(1.0)';
                e.currentTarget.style.boxShadow =
                  '0 6px 20px rgba(0, 0, 0, 0.25), 0 0 15px rgba(199, 242, 227, 0.6)';
              }}
            />
          </div>
        )}
      </div>

      {/* updated styles for zero top/bottom whitespace and visual balance */}
      <style jsx>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        html, body {
  margin: 0 !important;
  padding: 0 !important;
  width: 100%;
  height: 100%;
  min-height: 100%;
  background-color: #5b78b4 !important;
  overflow-x: hidden;
  overflow-y: auto;
  scroll-behavior: smooth;
  overscroll-behavior: none;
  background-attachment: fixed;
  box-sizing: border-box;
}

      main {
  height: 100%;
  min-height: 100vh;
  width: 100%;
  margin: 0;
  padding-top: 4rem;
  padding-bottom: 4rem;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  background-color: #5b78b4 !important;
  position: relative;
  box-sizing: border-box;
}

        /* absolute guarantee across iOS, Safari, and Chrome */
        @supports (height: 100svh) {
          html, body, main {
            height: 100svh;
            min-height: 100svh;
            background-color: #5b78b4 !important;
          }
        }
        .panda-container {
          display: flex;
          justify-content: center;
          align-items: center;
          margin-top: 2.5rem;
          margin-bottom: 1rem;
          animation: bounce 3s ease-in-out infinite;
        }

        label.field {
          margin-top: 1rem;
          margin-bottom: 2rem;
        }

        .panda {
          width: 160px;
          height: 160px;
        }
        .panda-spinner {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
}

.paw {
  width: 25px;
  height: 25px;
  background-color: #4CAF50;
  border-radius: 50%;
  position: relative;
  animation: pawBounce 1.2s infinite ease-in-out;
}

.paw::before,
.paw::after {
  content: "";
  position: absolute;
  background-color: #fff;
  border-radius: 50%;
}

.paw::before {
  width: 8px;
  height: 8px;
  top: 3px;
  left: 3px;
}

.paw::after {
  width: 5px;
  height: 5px;
  bottom: 3px;
  right: 3px;
}

.paw1 { animation-delay: 0s; }
.paw2 { animation-delay: 0.2s; }
.paw3 { animation-delay: 0.4s; }
.paw4 { animation-delay: 0.6s; }

@keyframes pawBounce {
  0%, 80%, 100% { transform: scale(0.8); opacity: 0.6; }
  40% { transform: scale(1.2); opacity: 1; }
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

        @media (min-width: 1024px) {
          main {
            justify-content: flex-start;
            padding-top: 3rem;
          }
          .panda-container {
            margin-top: 3rem;
          }
        }
         .fade-in-image {
          animation: fadeIn 1s ease-in-out;
          border: 6px solid #C7F2E3;
          background-color: #F9FFF9;
          padding: 8px;
          border-radius: 16px;
          transition: transform 0.3s ease, box-shadow 0.3s ease;
          cursor: pointer;
        }

        .fade-in-image:hover {
          transform: scale(1.05);
          box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        body::before {
          content: '';
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: #5b78b4;
          z-index: -1;
        }

      `}</style>
    </main>
  );
}
