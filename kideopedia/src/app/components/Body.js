"use client";

import { useState } from "react";
import { Input, Button, Image } from "@chakra-ui/react";
import { Baloo_2 } from "next/font/google";

const baloo = Baloo_2({ subsets: ["latin"], weight: ["700"] });

export default function Body() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState("local_user"); // fixed session ID for simplicity

  // --- Ask question (text or image) ---
  const handleAsk = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setAnswer("");
    setImageUrl("");
    const currentQuestion = question;
    setQuestion("");

    const endpoint = "http://localhost:8002/api/chat";

    try {
      const isImage = ["draw", "picture", "show", "image", "illustrate"].some((kw) =>
        currentQuestion.toLowerCase().includes(kw)
      );

      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: currentQuestion,
          session_id: sessionId,
          is_image_request: isImage,
        }),
      });

      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);

      const data = await res.json();

      if (data.image_url) setImageUrl(data.image_url);
      if (data.reply) setAnswer(data.reply);
    } catch (err) {
      console.error("Error:", err);
      setAnswer("Error: could not reach the backend.");
    } finally {
      setLoading(false);
    }
  };

  // --- Reset conversation ---
  const handleReset = async () => {
    if (!window.confirm("Start a new chat? Previous conversation will be lost.")) return;
    setLoading(true);
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
      setLoading(false);
    }
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-[#5b78b4] text-center">
      {/* Kidopedia Title */}
      <label
        className={baloo.className}
        style={{
          fontWeight: "700",
          fontSize: "3.4rem",
          color: "white",
          marginBottom: "2rem",
        }}
      >
        Kidopedia AI
      </label>

      {/* Input and Buttons */}
      <div className="flex flex-col items-center gap-4">
        <Input
          size="md"
          placeholder="Ask me anything"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          style={{ width: "250px", textAlign: "center", borderRadius: "50px" }}
        />
        <Button
          size="lg"
          colorScheme="green"
          onClick={handleAsk}
          disabled={loading}
        >
          {loading ? "Thinking..." : "Ask"}
        </Button>
        <Button size="sm" colorScheme="red" onClick={handleReset} disabled={loading}>
          New Chat
        </Button>
      </div>

      {/* Answer */}
      {answer && !loading && (
        <p style={{ color: "white", marginTop: "1.5rem", width: "70%" }}>
          <strong>Answer:</strong> {answer}
        </p>
      )}

      {/* Image */}
      {imageUrl && (
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
            onClick={() => window.open(imageUrl, "_blank")}
            style={{ cursor: "pointer", border: "4px solid #C7F2E3", padding: "4px" }}
          />
        </div>
      )}
    </main>
  );
}
