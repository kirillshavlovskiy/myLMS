import React from 'react';
import Editor from '@monaco-editor/react';

function MonacoEditor() {
    const customTheme = {
        base: 'vs-dark',
        language: "python",
        colors: {
            'editor.background': 'rgb(1, 1, 1)',
            'editor.foreground': 'rgb(255, 255, 255)',
        },
        rules: [
            { token: 'comment', foreground: '008000', fontStyle: 'italic' },
            { token: 'keyword', foreground: 'FFA500', fontStyle: 'bold' },
            // Define more rules for different syntax elements as needed
        ]
    };

    return (
        <div>
            <h1>Monaco Editor Example</h1>
            <Editor
                height="500px"
                width="700px"
                defaultLanguage="javascript"
                defaultValue="// Start coding!"
                theme={customTheme} // Pass the custom theme directly here
            />
        </div>
    );
}

export default MonacoEditor;