const input = document.getElementById("messageInput"); // ID of message box from html file
const button = document.getElementById("sendButton"); // ID of send button from html file
const responseBox = document.getElementById("response"); // ID of response box from html file

button.addEventListener("click", sendMessage); // Have to do something when button is clicked

async function sendMessage() {
  // What happen after button is clicked
  const userText = input.value; //JS reads user input
  try {
    const response = await fetch("http://localhost:8000/chat", {
      //JS sends HTTP request
      method: "POST", //Browser sends request to backend
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: userText }),
    });

    const data = await response.json(); //JS reads JSON
    responseBox.innerText = data.answer; //Frontend must match backend response schema exactly, JS updates UI
  } catch (error) {
    responseBox.innerText = "Error: " + error.message;
  }
}
