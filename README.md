# Chatbot Performance Evaluation Framework

This project provides a framework to evaluate the performance of chatbots using various metrics. The system leverages a local Langfuse server to retrieve and analyze traces from chatbot interactions, computing scores based on predefined operational and LLM-based metrics. The goal is to simulate both past and live environments, analyze chatbot performance, and visualize the results for meaningful insights. Importantly, the framework has been designed to run offline, with local server and local LLM instance.

## Features

- **Pre-Populated Trace**: Load previously saved traces into a Langfuse server for analysis.
- **Metrics Evaluation**: Compute scores for different metrics such as truthfulness, relevance, accuracy, response conciseness, hallucination, multi-query accuracy  and operational metrics like response time.
- **Visualization**: Visualize performance metrics, including mean scores by bot for each metric.
- **Simulation**: Simulate a live environment by fetching random traces, evaluating performance in real-time, and saving results.

  
## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/antoinebrias/llm_evaluation
    cd llm_evaluation
    ```

2. Include the LLM Model, the database and the previous traces

    You need to download the LLM model from HuggingFace and place it in the appropriate directory.

    For example, you can use the **Phi-3-mini-4k-instruct** model. Download the model from [this link](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/blob/main/Phi-3-mini-4k-instruct-q4.gguf).

    After downloading the model file, move it to the `gpt4all` directory in your project. 

    ``` mv Phi-3-mini-4k-instruct-q4.gguf gpt4all/   ```
 
    This ensures that the model is placed in the correct folder for use in your project.

    Additionally, make sure to include the `data.db` and `traces_export.csv` files, which are located in the `data` folder of the project. These files are required to run the evaluation framework.

    Make sure that your LLM model (for instance `Phi-3-mini-4k-instruct-q4.gguf`), `data.db` and `traces_export.csv`, are placed in their respective folders before proceeding to the next steps.

3. Build and run the Docker container:

    This project uses Docker to set up a local Langfuse server for trace retrieval. Build and run the Docker container using the following commands:

    ```bash 
    docker compose up
    ```

    This will download the necessary images, build the containers, and start the services (langfuse server and its postgresql database, and the python app).

4. Access the Langfuse Server

    Once the Docker container is up and running, open your web browser and navigate to the following URL:

    [http://localhost:4000](http://localhost:4000)

5. Login to the Langfuse Interface

    Use the following credentials to log into the Langfuse dashboard:

    - **Email**: `user@example.com` 
    - **Username**: `JohnDoe`
    - **Password**: `password123`
    
     In the Langfuse interface, navigate to the "llm-evaluation" project to view trace data and performance metrics. The dashboard will display real-time information on chatbot interactions, including message traces, response times, and relevant scores for different metrics.


## Usage

1. **Populate Langfuse traces**: 
   The `main.py` script first loads saved traces from the CSV file (`traces_export.csv`) into the Langfuse server. These traces have the name 'import' in Langfuse. The Session tag differentiates the two bots (ALX AiCE and Savanna).

2. **Visualization**:
   The results of the load traces are visualized through charts that show mean scores for each bot across the various evaluation metrics.

3. **Metrics Definition**:
   The framework supports both operational (i.e. non-LLM based metrics) and LLM-based metrics. The operational metrics focus on quantitative aspects (e.g., response time), while LLM-based metrics evaluate the quality of chatbot responses based on factors like truthfulness, relevance, accuracy, and conciseness.

4. **Bot Configuration**:
   The system simulates interactions with multiple chatbots, fetching random sample data from a database and evaluating them. You can define the number of samples and history depth for each bot configuration.

5. **Simulation**:
   Once the saved traces are populated, the system simulates a live environment by fetching new data, evaluating performance metrics, and visualizing the results. These traces have the name 'live' in Langfuse.

6. **Traces analysis**:
    The Langfuse interface provides tools for exploring and analyzing individual traces, allowing you to drill down into specific interactions. This includes details on response times, metrics scored, and other performance indicators for comprehensive trace analysis.


### Projet structure
      ├── data/ # Directory for data storage 

      ├── gpt4all/ # GPT-4All model files (or other models) 

      ├── src/ # Source code for the application 

      | ├── unit_tests/ # Unit tests for different components 

      | ├── .... (python files)       

      │ └── main.py # Main entry point for running the project 

      ├── requirements.txt # List of project dependencies 

      ├── .env # Environment variables (API keys, URLs)

      ├── .gitignore # Git ignore rules to exclude unnecessary files 

      ├── docker-compose.yml # Docker Compose file for multi-container setup 

      └── Dockerfile # Dockerfile for containerizing the app

- **`main.py`**: The entry point of the project, where the trace population, simulation, and evaluation occur.
- **`database_interface.py`**: Contains functions to connect to the database and fetch random data for evaluation.
- **`llm_interface.py`**: Contains functions to load the LLM model and query it.
- **`evaluation.py`**: Contains the function `evaluate_sample` that evaluates the chatbot traces based on different metrics.
- **`visualization.py`**: Contains functions to visualize evaluation results, such as `visualize_evaluation` and `visualize_score_means_by_bot`.
- **`traces_io.py`**: Functions to import traces from CSV files.
- **`config.py`**: Configuration file containing paths, database details, and other settings.

### Main Technologies Used

- **GPT-4All**: For message evaluation based on LLM-based metrics.
- **Langfuse**: For trace logging and monitoring chatbot interactions. A local server runs with a headless configuration to show the capabilities of the framework.
- **pandas**: For data manipulation and storage of evaluation results in DataFrames.
- **Matplotlib/Plotly**: For data visualization.
- **Logging**: Python’s built-in logging module is used for detailed logs.
- **SQL**: For fetching chatbot response data.
- **Unit Testing (unittest)**:  The project uses **unittest** for testing key components, with **unittest.mock** to mock external services like Langfuse and GPT-4All. 

## To-do list

- Fix metadata extraction. Sometime the metadata are badly formatted. Need to be fixed.
- Update and other metrics. They are currently based on sentiment analysis with 'negative','neutral','positive' output (converted to 0, 0.5, 1 ouptut values)

## Future Improvements

The project is designed with flexibility in mind, enabling future enhancements and integrations. Below are some key areas for future improvements:

### 1. **Fine-tuning Using ALX Internal Documents**

   - **Objective**: Leverage ALX's internal documents or any proprietary datasets to fine-tune the existing language model (LLM), improving its performance in response evaluation (accuracy for instance) or on specialized tasks.

### 2. **Exploring Other Models**

   - **Objective**: I was limited by the performances of my laptop and the use of a small local LLM. Investigate and integrate alternative language models to provide more flexibility and robustness to the application.

### 3. **Including Human Evaluation**
   - **Objective**: Human evaluation remains the gold standard in chatbot evaluation. Creating an evaluation module to collect user satisfaction may provide valuable insights.

### 4. **Including Other Metrics**
   - **Objective**: metrics related to a set of reference responses like (BLEU and ROUGE) may also improve the performances.

## Contact

For questions or feedback, feel free to reach out to me at antoinebrias@gmail.com.

