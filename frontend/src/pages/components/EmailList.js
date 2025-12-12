
import React from 'react';

export default function EmailList() {
  const emails = [
    { subject: "Invoice #123", category: "Billing" },
    { subject: "Login Info", category: "Account Info" }
  ];

  return (
    <div>
      {emails.map((email, index) => (
        <div key={index} className="border p-2 mb-2">
          <strong>{email.subject}</strong> - {email.category}
        </div>
      ))}
    </div>
  );
}
