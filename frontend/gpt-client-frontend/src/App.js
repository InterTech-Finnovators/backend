import React, { useState, useEffect, createContext } from 'react';
import { BrowserRouter as Router, Route, Routes, useNavigate } from 'react-router-dom';
import { Button, Input, Dropdown, Menu, Avatar } from 'antd';
import { SendOutlined, EllipsisOutlined, UserOutlined ,} from '@ant-design/icons';
import './normalize.css';
import './App.css';
import LoginForm from './Components/LoginForm/LoginForm'; // Correct import path
import RegisterForm from './Components/LoginForm/RegisterForm';
import ForgotPasswordForm from './Components/LoginForm/ForgotPasswordForm';
import ReactSwitch from "react-switch";

export const ThemeContext = createContext(null);
// const [theme, setTheme] = useState('light');

//   const toggleTheme = () => {
//     setTheme((curr) => (curr === "light" ? "dark" : "light"));
//   };

// Utility function to get time category
// Input: timestamp (Date object)
// Process: Calculates the time difference between the current time and the given timestamp
// Output: String indicating the time category ("Last Hour", "Today", "Yesterday", or date string)
const getTimeCategory = (timestamp) => {
  const now = new Date();
  const sessionDate = new Date(timestamp);
  const timeDifference = now - sessionDate;

  if (timeDifference < 3600000) {
    return "Last Hour";
  } else if (timeDifference < 86400000) {
    return "Today";
  } else if (timeDifference < 172800000) {
    return "Yesterday";
  } else {
    return sessionDate.toLocaleDateString();
  }
};

// Utility function to categorize sessions by time
// Input: sessions (Array of session objects)
// Process: Groups sessions into categories based on their timestamps
// Output: Object categorizing sessions by time
const categorizeSessions = (sessions) => {
  const categories = {};

  sessions.forEach((session) => {
    const category = getTimeCategory(session.timestamp);
    if (!categories[category]) {
      categories[category] = [];
    }
    categories[category].push(session);
  });

  return categories;
};

// Utility function to limit the length of session names
// Input: message (String)
// Process: Trims the message to the first 5 words and shortens it to 20 characters if needed
// Output: Shortened session title (String)
const getTitleFromMessage = (message) => {
  const words = message.split(" ");
  const title = words.slice(0, 5).join(" ");
  return title.length > 20 ? title.substring(0, 20) + "..." : title;
};

// SignOutButton Component
const SignOutButton = () => {
  const navigate = useNavigate();

  const handleSignOut = () => {
    localStorage.removeItem('token'); // Remove token from local storage
    navigate('/login'); // Redirect to login page
  };

  return (
    <Button
      onClick={handleSignOut}
      style={{ position: 'absolute', top: 30, right: 10, width: '100px' }}
      className="signOutButton"
    >
      Sign Out
    </Button>
  );
};


  
// MainScreen component
const MainScreen = () => {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [currentMessage, setCurrentMessage] = useState("");
  const [theme, setTheme] = useState('light');

  const toggleTheme = () => {
    setTheme((curr) => (curr === "light" ? "dark" : "light"));
  };

  useEffect(() => {
    const fetchChatHistory = async () => {
      const token = localStorage.getItem('token');
      try {
        const response = await fetch('http://localhost:8000/history', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        setSessions(data.chats.map(chat => ({
          title: chat.chat_id,
          messages: chat.history.flatMap(entry => [
            { text: entry.input, isUser: true, type: 'chatMessage' },
            { text: entry.response, isUser: false, type: 'chatMessageGpt4' },
          ]),
          timestamp: new Date(), // Placeholder, set this appropriately if available
        })));
      } catch (error) {
        console.error('Error fetching chat history:', error);
      }
    };

    fetchChatHistory();
  }, []);

  const handleSendMessage = async () => {
    if (currentMessage.trim() !== "" && !/^[\s\t\n]/.test(currentMessage)) {
      let newSessions = [...sessions];
      let responseMessage = "";
      const messageToSend = currentMessage;
      setCurrentMessage(""); // Clear the input bar immediately
  
      if (currentSession === null) {
        const newTitle = getTitleFromMessage(messageToSend);
        const timestamp = new Date();
        const newSession = {
          messages: [{ text: messageToSend, isUser: true, type: 'chatMessage' }],
          title: newTitle,
          timestamp
        };
        newSessions.push(newSession);
        setCurrentSession(newSessions.length - 1);
  
        // Send the message to the API and get the response
        responseMessage = await getApiResponse(messageToSend, newSessions.length - 1);
        newSession.messages.push({ text: responseMessage, isUser: false, type: 'chatMessageGpt4' });
      } else {
        if (newSessions[currentSession]) {
          newSessions[currentSession].messages.push({ text: messageToSend, isUser: true, type: 'chatMessage' });
  
          // Send the message to the API and get the response
          responseMessage = await getApiResponse(messageToSend, currentSession);
          newSessions[currentSession].messages.push({ text: responseMessage, isUser: false, type: 'chatMessageGpt4' });
        }
      }
      setSessions(newSessions);
    }
  };

  const handleNewSession = () => {
    setCurrentMessage("");
    setCurrentSession(null);
  };

  const handleSwitchSession = (index) => {
    setCurrentSession(index);
  };

  const handleDeleteSession = (index) => {
    if (sessions.length === 1) {
      return; // Prevent deleting the last remaining session
    }

    const newSessions = sessions.filter((_, i) => i !== index);
    setSessions(newSessions);

    if (currentSession === index) {
      setCurrentSession(null); // Reset current session
    } else if (currentSession > index) {
      setCurrentSession(currentSession - 1);
    }
  };

  const handleRenameSession = (index, newName) => {
    if (newName.trim() !== "" && !/^[\s\t\n]*$/.test(newName)) {
      const newSessions = [...sessions];
      newSessions[index].title = newName;
      setSessions(newSessions);
    }
  };

  const generateUniqueSessionTitle = (sessions) => {
    const existingNumbers = sessions
      .map(session => session.title)
      .filter(title => title.startsWith("FinLitAI "))
      .map(title => parseInt(title.replace("FinLitAI ", ""), 10))
      .filter(number => !isNaN(number));

    const maxNumber = existingNumbers.length > 0 ? Math.max(...existingNumbers) : 0;
    return `FinLitAI ${maxNumber + 1}`;
  };

  const getApiResponse = async (message, sessionId) => {
    const token = localStorage.getItem('token');
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          input: message,
          chat_id: `session-${sessionId}`
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('Error fetching API:', error);
      return null;
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === "Enter") {
      handleSendMessage();
    }
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    if (!/^[\s\t\n]/.test(value)) {
      setCurrentMessage(value);
    }
  };

  const menu = (index) => (
    <Menu>
      <Menu.Item onClick={() => handleRenameSession(index, prompt("Enter new name").trim())}>
        Rename
      </Menu.Item>
      <Menu.Item onClick={() => handleDeleteSession(index)} disabled={sessions.length === 1}>
        Delete
      </Menu.Item>
    </Menu>
  );

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
    <div className={`App ${theme}`} id={theme}>
      <aside className="sideMenu" id={theme}>
        <div className="newSessionButton" onClick={handleNewSession }id={theme}>
          + New FinLitAI
        </div>
        {Object.entries(categorizeSessions(sessions)).map(([category, sessionsInCategory]) => (
          <div key={category}>
            <div className="categoryHeader" id={theme}>{category}</div>
            {sessionsInCategory.map((session, index) => (
              <div key={index} className="sideMenuButton"id={theme}>
                <span className="sessionName" id={theme} onClick={() => handleSwitchSession(sessions.indexOf(session))}>
                  {session.title}
                </span>
                <Dropdown overlay={menu(sessions.indexOf(session))} trigger={['click']}>
                  <Button className="deleteButton" id={theme} icon={<EllipsisOutlined />} />
                </Dropdown>
              </div>
            ))}
          </div>
        ))}
      </aside>
  
      <section className="chatBox">
        <div className="chatLog">
          <div className="chatMessageGpt4">
            <div className="chatMessageAligner gpt">
              <div className="avatarGpt"></div>
              <div className="message" id={theme}>
                Ask me anything! I am here to help you.
              </div>
            </div>
          </div>
  
          {currentSession !== null && sessions[currentSession] && sessions[currentSession].messages.map((msg, index) => (
            <div key={index} className={msg.type}>
              <div className={`chatMessageAligner ${msg.isUser ? 'user' : 'gpt'}`}>
                {msg.isUser ? (
                  <Avatar className="avatar" size="large" icon={<UserOutlined />} />
                ) : (
                  <div className="avatarGpt"></div>
                )}
                <div className="message">{msg.text}</div>
              </div>
            </div>
          ))}
        </div>
        
        
  
        <div className="chatInputBar">
          <Input.TextArea
            className="ChatInputWriteHere"
            rows={1}
            placeholder="You Can Write Here"
            value={currentMessage}
            onChange={handleInputChange}
            onPressEnter={handleKeyPress}
            autoSize={{ minRows: 1, maxRows: 6 }}
            id={theme}
          />
          <Button
            className="sendButton"
            shape="circle"
            icon={<SendOutlined />}
            onClick={handleSendMessage}
            id={theme}
          />
        </div>
        <p className="warningMessage">
          FinLitAI is a Finnovators bot and may make mistakes!
        </p>
      </section>
      <SignOutButton id={theme}/>
      <div className="switch" id={theme}>
          
          <ReactSwitch onChange={toggleTheme} checked={theme === "dark"} />
          
        </div>
    </div>
    </ThemeContext.Provider>
  );  
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginForm />} />
        <Route path="/register" element={<RegisterForm />} />
        <Route path="/forgot-password" element={<ForgotPasswordForm />} />
        <Route path="/chat" element={<MainScreen />} />
        <Route path="/" element={<LoginForm />} />
      </Routes>
    </Router>
  );
}

export default App;