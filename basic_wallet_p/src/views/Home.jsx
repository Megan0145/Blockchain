import React, { useEffect, useState, useRef } from "react";
import styled from "styled-components";
import axios from "axios";

const StyledHome = styled.div`
    display: flex;
    flex-direction column;
    justify-content: center;
    align-items: center;
    margin-top: 2rem;
    .container {
        width: 100%;
        display: flex;
        .wallet, .send_coin {
            width: 50%;
            padding: 2rem;
            display: flex; 
            flex-direction: column;
            align-items: center;
        }
    }
`;

export default function Home(props) {
  const [chain, setChain] = useState([]);
  const [userId, setUserId] = useState("");
  let balance = 0;
  let outgoing_transactions = [];
  let incoming_transactions = [];
  const userIdRef = useRef();
  const payeeIdRef = useRef();

  useEffect(() => {
    axios
      .get("http://localhost:5000/chain")
      .then(res => {
        setChain(res.data.chain);
        console.log(res.data.chain);
      })
      .catch(err => console.log(err));
  }, [userId, balance]);

  const makePayment = () => {
      axios.post("http://localhost:5000/transactions/new",{
          "sender": userId,
          "recipient": payeeIdRef.current.value,
          "amount": 1
      })
      .then(res => {
          console.log(res)
          balance -= 1;
          outgoing_transactions.push({
            "sender": userId,
            "recipient": payeeIdRef.current.value,
            "amount": 1
        })
      })
      .catch(err => {
          console.log(err)
      })
  }

  return (
    <StyledHome>
      <h1>Welcome to your LambdaCoin Wallet {userId}</h1>
      <input placeholder="Enter your user id" ref={userIdRef} />
      <button onClick={() => setUserId(userIdRef.current.value)}>Go</button>
      <div className="container">
        <div className="wallet">
          {!chain.length > 0
            ? null
            : chain.map(block => {
                block.transactions.map(transaction => {
                  if (userId === transaction.recipient) {
                    balance += transaction.amount;
                    incoming_transactions.push(transaction);
                    console.log(balance);
                    console.log(incoming_transactions);
                  }
                  if (userId === transaction.sender) {
                    balance -= transaction.amount;
                    outgoing_transactions.push(transaction);
                    console.log(balance);
                    console.log(outgoing_transactions);
                  }
                });
              })}
          <h3>Balance: {balance}</h3>
          <h3>Outgoing transactions:</h3>
          {outgoing_transactions.map(transaction => (
            <>
              <p>Recipient: {transaction.recipient}</p>
              <p>Amount: {transaction.amount}</p>
            </>
          ))}
          <h3>Incoming transactions:</h3>
          {incoming_transactions.map(transaction => (
            <>
              <p>
                Sender:{" "}
                {transaction.sender === "0" ? "mined" : transaction.sender}
              </p>
              <p>Amount: {transaction.amount}</p>
            </>
          ))}
        </div>
        <div className="send_coin">
            <h3>Send a LambdaCoin to another user:</h3>
           <input ref={payeeIdRef} placeholder="ID of payee"/>
           <button onClick={() => makePayment()}>Go</button>
        </div>
      </div>
    </StyledHome>
  );
}
