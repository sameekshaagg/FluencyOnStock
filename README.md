# Company Name Fluency Score  

This repository contains the code, data preparation scripts, and LaTeX files used in my thesis on **the relationship between company name fluency and firm outcomes** (valuation, liquidity, and performance). The repository is organized into modular folders, each corresponding to a key part of the project.  

---

## Repository Structure  

### 📂 Data_prep  
- Contains the Python scripts used to clean and transform the raw data into a format suitable for the neural network and subsequent regression analysis.  
- **Data Access**: Due to size constraints, the full dataset is hosted externally and can be downloaded from:  
  [Google Drive link](https://drive.google.com/drive/folders/1QtdJiX9Hw5gCjpyesIs6BrrZW-I_ahN3?usp=sharing)  

---

### 📂 Neural_network  
- Includes all files related to the neural network architecture and training process.  
- Contains:  
  - Implementation of different models.  
  - Best-performing model saved for replication.  
  - Hyperparameter search results.  

---

### 📂 Liquidity  
- Python scripts to construct the dataset used for liquidity regressions.  
- Instructions on how the fluency score is merged with control variables.  
- Stata `.do` files for running the regression analysis.  

---

### 📂 Valuation  
- Similar to the *Liquidity* folder but focused on firm valuation outcomes.  
- Contains Python preprocessing scripts and Stata regression files.  

---

### 📂 Performance  
- Focused on firm performance measures.  
- Includes Python preprocessing scripts and corresponding Stata `.do` files for regression analysis.  

---

### 📂 LaTeX  
- Contains all files related to the thesis write-up.  
- **figures/**: All plots and visualizations used in the thesis.  
- **bibliography.bib**: BibTeX reference file containing all cited works.  
- **main.tex**: The LaTeX source file of the thesis.  

---

## Notes  
- The code is primarily written in **Python (TensorFlow, Keras, Pandas, etc.)** and **Stata**.  
- Both data preparation and regression steps are included to allow full replication of the results.  
- The fluency score dataset covers **15,274 companies**, with quarterly stock characteristics collected between **1980–2024**.  

---

👉 This structure allows anyone to reproduce, understand, or extend the analysis with minimal effort.  
