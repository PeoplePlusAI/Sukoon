import React, { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async () => {
    if (input.trim() === '') return;

    setMessages([...messages, { text: input, user: true }]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: input }),
      });

      const data = await response.json();
      setMessages(prevMessages => [...prevMessages, { text: data.full_output.agent_out.output, user: false }]);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      {/* <div className="messages-container">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.user ? 'user-message' : 'bot-message'}`}>
            <p>{message.text}</p>
          </div>
        ))}
        {isLoading && (
          <div className="loading-container">
            <div className="loading-bar"></div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
        />
        <button onClick={handleSend}>Send</button>
      </div> */}

      <div className="chat-container" style={{ display: "flex" }}>
        <div className="menu">
          <div className="button" style={{ textAlign: "center" }}>
            <i className="fa-regular fa-square-plus" style={{ fontSize: "20px" }}></i>
            <p style={{ margin: 0 }}>New</p>
          </div>
          <div className="button" style={{ textAlign: "center" }}>
            <i className="fa-solid fa-wand-magic-sparkles" style={{ fontSize: "20px" }}></i>
            <p style={{ margin: 0 }}>Discover</p>
          </div>
          <div className="button" style={{ textAlign: "center" }}>
            <i className="fa-regular fa-user" style={{ fontSize: "20px" }}></i>
            <p style={{ margin: 0 }}>Profile</p>
          </div>
        </div>
        <div className="menu-content">
          <h4 style={{ padding: "5px" }}>Discover Chats</h4>
          <div className="row discover">
            <div className="col-6">
              {/* <img src="./img/image3.png" alt="Discover 2" /> */}
              <img src="./img/img1.png" alt="" />
            </div>
            <div className="col-6">
              <img src="./img/image3.png" alt="" />
            </div>
            <div className="col-12">
              <img src="./img/Frame 4.png" alt="" />
            </div>
          </div>
        </div>
        <div className="chatConv pt-4 pe-4">
          <div className="mx-auto" style={{ width: "60%" }}>
            <div className="messages pt-5 mt-4 mx-auto" style={{ height: "75vh" }}>
              {messages.map((message, index) => (
                <p key={index} className={`small p-2 me-3 my-1 rounded-3 ${message.user ? 'bg-primary text-white userMsg' : 'agentMsg'}`}>{message.text}</p>
              ))}
              {isLoading && (
                <div className="loading-container">
                  <div className="loading-bar"></div>
                </div>
              )}
              {/* <p className="small p-2 me-3 my-1 text-white rounded-3 bg-primary userMsg">I need peace of mind!</p>
              <p className="small p-2 ms-5 my-1 mt-4 rounded-3 text-dark agentMsg">That’s a great goal to have. I hope
                this project will bring some peace of mind to the people who use it. What kind of features are
                you planning to include? 😊</p> */}
            </div>
            <div className="chatAction">
              <div className="row mx-auto query-action">
                <div className="input-group mb-3">
                  <div className="form-floating">
                    <input type="text" className="w-100 h-100" id="floatingInputGroup1"
                      placeholder="Type your message..." value={input} onChange={(e) => setInput(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && handleSend()} /></div><span
                        className="input-group-text d-flex justify-content-center submit" onClick={handleSend}><i
                          className="fa-solid fa-arrow-up"></i>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;