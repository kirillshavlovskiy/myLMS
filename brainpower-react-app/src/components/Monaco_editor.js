import React, { useEffect, useState } from 'react';
import Editor, { useMonaco } from '@monaco-editor/react';
import { Button, TextField, Select, MenuItem } from '@mui/material';



const MonacoEditorComponent = () => {
    const monaco = useMonaco();
    const [selectedTheme, setSelectedTheme] = useState('Cobaltnew');
    const [isThemeLoaded, setIsThemeLoaded] = useState(false);
    const [themeData, setThemeData] = useState(null);
    const availableThemes = {
        Cobaltnew: 'Cobaltnew.json',
        GitHubDark: 'GitHubDark.json',
        Monokai: 'Monokai.json',
        Sunburst: 'Sunburst.json',
        Merbivore: 'Merbivore.json',
    };

    useEffect(() => {
        if (!monaco) return;
        const defaultTheme = 'Cobaltnew';
        const themeToLoad = selectedTheme && availableThemes[selectedTheme] ? selectedTheme : defaultTheme;
        import(`./monaco-themes-master/themes/${availableThemes[themeToLoad]}`)
            .then((data) => {
                monaco.editor.defineTheme(themeToLoad, data);
                setIsThemeLoaded(true);
            })
            .catch((error) =>
                console.error('An error occurred while loading the theme:', error)
            );
    }, [selectedTheme, monaco, availableThemes]);

    const handleChange = (event) => {
        setSelectedTheme(event.target.value);
    };

    return (
        <div style={{ width: '100vw', height: '100vh' }}>
            <Select value={selectedTheme} onChange={handleChange}>
                {Object.keys(availableThemes).map((theme) => (
                    <MenuItem key={theme} value={theme}>{theme}</MenuItem>
                ))}
            </Select>
            <Editor
                onChange={handleChange}
                height="calc(100vh - 40px)"
                defaultLanguage="javascript"
                defaultValue="// Place your code here"
                theme={isThemeLoaded ? selectedTheme : 'vs-dark'}
                options={{
                    fontSize: 16,
                    fontFamily: 'monospace',
                    minimap: {
                        enabled: true,
                    },
                    acceptSuggestionOnCommitCharacter: true,
                    acceptSuggestionOnEnter: 'on',
                    accessibilitySupport: 'auto',
                    autoIndent: false,

                    automaticLayout: true,

                    codeLens: true,
                  colorDecorators: true,
                  contextmenu: true,
                  cursorBlinking: "blink",
                  cursorSmoothCaretAnimation: false,
                  cursorStyle: "line",
                  disableLayerHinting: false,
                  disableMonospaceOptimizations: false,
                  dragAndDrop: false,
                  fixedOverflowWidgets: false,
                  folding: true,
                  foldingStrategy: "auto",
                  fontLigatures: false,
                  formatOnPaste: false,
                  formatOnType: false,
                  hideCursorInOverviewRuler: false,
                  highlightActiveIndentGuide: true,
                  links: true,
                  mouseWheelZoom: false,
                  multiCursorMergeOverlapping: true,
                  multiCursorModifier: "alt",
                  overviewRulerBorder: true,
                  overviewRulerLanes: 2,
                  quickSuggestions: true,
                  quickSuggestionsDelay: 100,
                  readOnly: false,
                  renderControlCharacters: false,
                  renderFinalNewline: true,
                  renderIndentGuides: true,
                  renderLineHighlight: "all",
                  renderWhitespace: "none",
                  revealHorizontalRightPadding: 30,
                  roundedSelection: true,
                  rulers: [],

                  scrollBeyondLastColumn: 5,
                  renderIndentGuides: false,
                  scrollBeyondLastColumn: 5,
                  scrollBeyondLastLine: true,
                  selectOnLineNumbers: true,
                  selectionClipboard: true,
                  selectionHighlight: true,
                  showFoldingControls: "mouseover",
                  smoothScrolling: false,
                  suggestOnTriggerCharacters: true,
                  wordBasedSuggestions: true,
                  wordSeparators: "~!@#$%^&*()-=+[{]}|;:'\",.<>/?",
                  wordWrap: "off",
                  wordWrapBreakAfterCharacters: "\t})]?|&,;",
                  wordWrapBreakBeforeCharacters: "{([+",
                  wordWrapBreakObtrusiveCharacters: ".",
                  wordWrapColumn: 80,
                  wordWrapMinified: true,
                  wrappingIndent: "none"
                  }}
            />
        </div>
    );
};

export default MonacoEditorComponent;