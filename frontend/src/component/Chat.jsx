import React, { useState, useEffect, useRef } from 'react';
import './styles/Chat.css';
import { FaMicrophone } from "react-icons/fa";
import axios from 'axios'

const Chat = () => {
  const [chatRecord, setChatRecord] = useState([]);
  const [transcript, setTranscript] = useState('');
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);
  const interimTranscript = useRef('');
  const [isSpeaking, setIsSpeaking] = useState(false);

  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState([]);
  const chatContainerRef = useRef(null);

  const retrieveRecords = async () => {
    try {
      const res = await axios.get(`http://localhost:8000/api/chats/`)
      setChatRecord(res.data.chats[0].messages)
    } catch (e) {
      console.log(e)
    }
  }

  const sendNewChat = async (message) => {
    try {
      const formData = { message: message, sender: "User" }
      const res = await axios.post(`http://localhost:8000/api/chats/6731ee2f2e118cfd5f9f9bae/messages/`, formData, {
        headers: {
          'Content-Type': 'application/json', 
        }
      })
      setMessages((prevMessages) => [...prevMessages, { content: res.data.message, sender: res.data.sender }])

      if (res.data.message.trim()) {
        const speech = new SpeechSynthesisUtterance(res.data.message);
        speech.lang = "en-US";
        speech.pitch = 1; 
        speech.rate = 1; 
  
        speech.onstart = () => setIsSpeaking(true);
        speech.onend = () => setIsSpeaking(false);
  
        window.speechSynthesis.speak(speech);
      }
    } catch (e) {
      console.log(e)
    }
  }

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    retrieveRecords()
  }, [])

  useEffect(() => {
    setMessages([])
    chatRecord.map((chat) => {
      setMessages((prevMessages) => [...prevMessages, { content: chat.message, sender: chat.sender }])
    })
  }, [chatRecord])

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleKeyDown = (newMessage) => {
    if (!(newMessage == '')) {
      setMessages((prevMessages) => [...prevMessages, { content: newMessage, sender: "User" }]);
      setInputValue('');
    }
  };

  useEffect(() => {
    if (!('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
      console.log("Speech Recognition API is not supported in this browser.");
      return;
    }

    recognitionRef.current = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    const recognition = recognitionRef.current;
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {

      interimTranscript.current = Array.from(event.results)
        .map((result) => result[0].transcript)
        .join('');
      console.log(interimTranscript.current)
    };

    recognition.onerror = (event) => {
      console.log('Speech recognition error:', event);
      setIsListening(false);
    };

    recognition.onend = () => {
      setTranscript((prevTranscript) => prevTranscript + ' ' + interimTranscript.current);
      sendNewChat(interimTranscript.current)
      // interimTranscript.current = '';
      setIsListening(false);
    };

    return () => {
      recognition.stop();
    };
  }, []);

  useEffect(() => {
    handleKeyDown(transcript)
  }, [transcript])

  useEffect(() => {
    console.log(messages)
  }, [messages])

  useEffect(() => {
    const recognition = recognitionRef.current;
    if (isListening) {
      setTranscript('');
      recognition.start();
    } else {
      recognition.stop();
    }
  }, [isListening]);

  const toggleListening = () => {
    setIsListening((prevState) => !prevState);
  };

  return (
    <div className='dashboard-content__container'>
      <div className="chat-main__container">
        <div className="chat-header">
          <div>PyChat {isListening ? 'Stop Listening' : 'Start Listening'}</div>
        </div>
        <div className="chat-log__container" ref={chatContainerRef}>
          {
            messages.map((message) => {
              return (
                message.sender === 'User' ? (
                  <div className="user-message">
                    <div className="chat-content">
                      {message.content}
                    </div>
                  </div>
                ) : (
                  <div className="pychat-message">
                    <div className="chat-content">
                      {message.content}
                    </div>
                  </div>
                )
              );
            })
          }

        </div>
        <div className="chat-controls__container">
          <input type="text" className='custom-input' placeholder='Send a message...' value={transcript} onChange={() => handleInputChange()} />
          <div className="chat-controls__buttons">
            <button className={`control-button ${isListening ? 'active' : ''}`} onClick={toggleListening}>
              <FaMicrophone />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;