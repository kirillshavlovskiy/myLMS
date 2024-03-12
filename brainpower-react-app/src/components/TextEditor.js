import React, { useState } from 'react';
import { Editor, EditorState } from 'draft-js';
import 'draft-js/dist/Draft.css';

function TextEditor() {
  const [editorState, setEditorState] = useState(() => EditorState.createEmpty());

  const handleChange = (newEditorState) => {
    setEditorState(newEditorState);
  };

  return (
    <div>
      <h2>My Text Editor</h2>
      <div style={{ border: '1px solid #ccc', minHeight: '200px', padding: '10px' }}>
        <Editor editorState={editorState} onChange={handleChange} />
      </div>
    </div>
  );
}

export default TextEditor;
