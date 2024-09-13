# Headline-Equality

Headline-Equality is an artificial intelligence headline analyzer designed to detect gender bias, sexism, and misogyny in the media. The idea behind this project is to visualize the sexism and misogyny present in the media so that we become more aware of how information is presented to us and the roles this perpetuates.

## Description

The system is built using Python and Streamlit for interactive visualization. It employs LangChain and advanced AI models like GEMMA 2 9B, LLaMA 3.1 7B, and GPT-4o-mini to analyze and detect patterns of gender bias in news headlines.

## Features

- **Headline Analysis**: Detects and classifies gender bias, sexism, and misogyny in news headlines.
- **Self-Validation System**: Incorporates a adversarial language models (LLMs) discuss and challenge the categorization of bias, ensuring more accurate and reliable results.
- **Headline Validation**: Offers the possibility to validate headline wording and suggest rewrites in different tones.
- **Headline Publication on X**: Allows publishing of validated headlines on X.com (formerly Twitter).
- **Interactive Visualization**: Dashboard to explore analysis results in a visual and interactive manner.

## Technologies Used

- **Programming Language**: Python
- **Visualization Framework**: Streamlit
- **AI Framework**: LangChain
- **AI Models**: GEMMA2 9B, LLaMA3.1 7B, GPT-4o-mini

## Used

```
# Interactive mode
streamlit run Home.py
```

```
# Only analyzer script
python analyzer.py
```


## Contributing

Contributions are welcome! If you want to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/new-feature`).
3. Make the necessary changes and commit (`git commit -am 'Add new feature'`).
4. Push the changes to the branch (`git push origin feature/new-feature`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
