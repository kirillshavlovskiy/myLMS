import React, { useState } from 'react';

function LandingPage() {
  const [answers, setAnswers] = useState({
    question1: '',
    question2: '',
    question3: '',
  });

  const handleQuestionChange = (event) => {
    const { name, value } = event.target;
    setAnswers((prevAnswers) => ({
      ...prevAnswers,
      [name]: value,
    }));
  };

  const handleSubmit = () => {
    // Send answers to the server
    console.log('Answers:', answers);
    // You can make an API call here to send the answers to the server
  };

  return (
    <div>
      <h1>Welcome to the Landing Page!</h1>
      <div>
        <h2>Question 1: Choose multiple options</h2>
        <select
          name="question1"
          value={answers.question1}
          onChange={handleQuestionChange}
          multiple
        >
          <option value="option1">Option 1</option>
          <option value="option2">Option 2</option>
          <option value="option3">Option 3</option>
        </select>
      </div>
      <div>
        <h2>Question 2: Choose one option</h2>
        <select
          name="question2"
          value={answers.question2}
          onChange={handleQuestionChange}
        >
          <option value="optionA">Option A</option>
          <option value="optionB">Option B</option>
          <option value="optionC">Option C</option>
        </select>
      </div>
      <div>
        <h2>Question 3: Write something</h2>
        <textarea
          name="question3"
          value={answers.question3}
          onChange={handleQuestionChange}
        />
      </div>
      <button onClick={handleSubmit}>Submit Answers</button>
    </div>
  );
}

export default LandingPage;
