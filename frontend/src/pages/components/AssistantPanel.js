
import React, { useState } from 'react';

export default function AssistantPanel() {
  const [chat, setChat] = useState("");

  const handleSend = () => {
    alert(`GPT Reply: Drafting response for "${chat}"`);
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-2">Assistant</h2>
      <div className="mb-4">
        <button className="bg-blue-500 text-white px-4 py-2 mr-2">Summarize Email</button>
        <button className="bg-green-500 text-white px-4 py-2 mr-2">Draft Reply</button>
        <button className="bg-yellow-500 text-white px-4 py-2">Mark Important</button>
      </div>
      <input
        type="text"
        placeholder="Ask GPT..."
        value={chat}
        onChange={(e) => setChat(e.target.value)}
        className="border p-2 w-full"
      />
      <button onClick={handleSend} className="bg-purple-500 text-white px-4 py-2 mt-2">Send</button>
    </div>
  );
}
