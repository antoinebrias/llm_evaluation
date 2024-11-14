# Chatbot Performance Evaluation Framework

This project provides a framework to evaluate the performance of chatbots using various metrics. The system leverages a local Langfuse server to retrieve and analyze traces from chatbot interactions, computing scores based on predefined operational and LLM-based metrics. The goal is to simulate both past and live environments, analyze chatbot performance, and visualize the results for meaningful insights.

## Features

- **Pre-Populated Trace**: Load previously saved traces into a Langfuse server for analysis.
- **Metrics Evaluation**: Compute scores for different metrics such as truthfulness, relevance, accuracy, response conciseness, hallucination, multi-query accuracy  and operational metrics like response time.
- **Visualization**: Visualize performance metrics, including mean scores by bot for each metric.
- **Simulation**: Simulate a live environment by fetching random traces, evaluating performance in real-time, and saving results.

## Project Structure

- **`main.py`**: The entry point of the project, where the trace population, simulation, and evaluation occur.
- **`database_interface.py`**: Contains functions to connect to the database and fetch random data for evaluation.
- **`evaluation.py`**: Contains the function `evaluate_sample` that evaluates the chatbot traces based on different metrics.
- **`visualization.py`**: Contains functions to visualize evaluation results, such as `visualize_evaluation` and `visualize_score_means_by_bot`.
- **`traces_io.py`**: Functions to import traces from CSV files.
- **`config.py`**: Configuration file containing paths, database details, and other settings.
  
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
    docker-compose build  
    docker-compose up
    ```

    This will download the necessary images, build the containers, and start the services (langfuse server and its postgresql database, and the python app).



## Usage

1. **Populate Langfuse traces**: 
   The `main.py` script first loads saved traces from the CSV file (`traces_export.csv`) into the Langfuse server.

2. **Metrics Definition**:
   The framework supports both operational (i.e. non-LLM based metrics) and LLM-based metrics. The operational metrics focus on quantitative aspects (e.g., response time), while LLM-based metrics evaluate the quality of chatbot responses based on factors like truthfulness, relevance, accuracy, and conciseness.

3. **Bot Configuration**:
   The system simulates interactions with multiple chatbots, fetching random sample data from a database and evaluating them. You can define the number of samples and history depth for each bot configuration.

4. **Simulation**:
   Once the saved traces are populated, the system simulates a live environment by fetching new data, evaluating performance metrics, and visualizing the results.

5. **Visualization**:
   The results are visualized through graphs and charts that show mean scores for each bot across the various evaluation metrics.


## Contact

For questions or feedback, feel free to reach out to me at antoinebrias@gmail.com.

