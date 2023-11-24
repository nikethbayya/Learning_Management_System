import {
  Avatar,
  ChatContainer,
  Conversation,
  ConversationHeader,
  ConversationList,
  MainContainer,
  Message,
  MessageInput,
  MessageList,
  MessageSeparator,
  Sidebar
} from "@chatscope/chat-ui-kit-react";

import "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";
import axios from "axios";
import { useEffect, useState } from "react";
import { useSelector } from 'react-redux';
import AppHeader from "../components/AppHeader";
import { socket } from "../socket";



function ChatPage() {
  const userInfo = useSelector((state) => state.user.userInfo)

  const [messageInputValue, setMessageInputValue] = useState("");
  const [chatSideBar, setChatSideBar] = useState({})
  const [chatHeader, setChatHeader] = useState({})
  const [chatConversation, setChatConversation] = useState([])

  useEffect(() => {
    axios
    .get('/chatRooms/all')
    .then((res) => {
      setChatSideBar(res.data)
      console.log(res.data)
      if (res.data.course_rooms.length > 0) {
        conversationChanged(res.data.course_rooms[0].room_id, res.data.course_rooms[0].room_name)
      }
    })
    .catch((err) => {
      console.log(err)
    })
  }, [setChatSideBar])

  useEffect(() => {
    function onReceiveMessage(message) {
      if (message.room_id !== chatHeader.room_id) {
        return;
      }
      const newChatConversation = [...chatConversation]
      newChatConversation.push( {
        message: message.content,
        sentTime: message.sentTime,
        sender: message.sender,
        sender_id: message.sender_id
      })
      setChatConversation(newChatConversation)
    }

    socket.on('receive_message', onReceiveMessage);

    return () => {
      socket.off('receive_message', onReceiveMessage);
    };
  }, [chatConversation, chatHeader.room_id]);

  const conversationChanged = (room_id, room_name) => {
    setChatHeader({
      name: room_name,
      room_id: room_id
    })
    axios.get('/chatMessages/' + room_id)
    .then((res) => {
      const {messages} = res.data
      setChatConversation(messages)
    })
    .catch((err) => {
      console.log(err)
    })
  }

  const messageSent = () => {
    socket.emit('send_message', {content: messageInputValue, room_id: chatHeader.room_id})
    setMessageInputValue('')
    
  }
  return (
    <div
      className="page-container"
      style={{
        height: "94vh",
        position: "relative",
      }}
    >
      <AppHeader />
      <MainContainer responsive>
        <Sidebar position="left" scrollable={false}>
          <ConversationList>
            <h3 style={{ marginLeft: 10 }}> Classes </h3>
            {chatSideBar["course_rooms"] && chatSideBar["course_rooms"].map((item, index) => {
              return (
                <Conversation
                  onClick={(event) => conversationChanged(item.room_id, item.room_name)}
                  key={'group_' + index}
                  name={item.room_name}
                  lastSenderName={item.lastSenderName}
                  info={item.info}
                  status={'available'}
                  unreadCnt={item.unreadCnt}
                >
                </Conversation>
              );
            })}
            {/* <h3 style={{ marginLeft: 10 }}> Direct Messages </h3>
            {chatSideBar["direct_rooms"] && chatSideBar["direct_rooms"].map((item, index) => {
              return (
                <Conversation
                  onClick={(event) => conversationChanged(item.room_id, item.room_name)}
                  key={'direct_' + index}
                  name={item.name}
                  lastSenderName={item.lastSenderName}
                  info={item.info}
                  status={item.status}
                  unreadCnt={item.unreadCnt}
                >
                </Conversation>
              );
            })} */}
          </ConversationList>
        </Sidebar>

        <ChatContainer>
          <ConversationHeader>
            <ConversationHeader.Back />
            <ConversationHeader.Content
              userName={chatHeader.name}
              info={chatHeader.info}
            />
          </ConversationHeader>
          <MessageList>
            {
              chatConversation.map((item, index) => {
                if (item.sender === "Admin") {
                  return (
                    <MessageSeparator key={'chat_msg_' + index}>
                      {'Admin says ' + item.message}
                    </MessageSeparator>
                  )
                }
                return (
                  <Message
                    key={'chat_msg_' + index}
                    model={{
                      message: item.message,
                      sentTime: item.sentTime,
                      sender: item.sender,
                      direction: (item.sender_id === userInfo.id) ? 'outgoing': 'incoming',
                      postion: 'normal'
                    }}
                  >
                    <Avatar src={'https://ui-avatars.com/api/?name=' + item.sender} name={item.sender} />
                    {/* <Message.Header sender={item.sender} sentTime={item.sentTime} /> */}
                  </Message>
                )
              })
            }
          </MessageList>
          <MessageInput
            placeholder="Type message here"
            value={messageInputValue}
            onChange={(val) => setMessageInputValue(val)}
            onSend={() => messageSent()}
            attachButton={false}
          />
        </ChatContainer>
      </MainContainer>
    </div>
  );
}

export default ChatPage;
