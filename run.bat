@echo off
echo Running Script 1
".venv\Scripts\python" "G:\Projetinhos\Patrimonio\notebooks\0- consolida.py"
echo Running Script 2
".venv\Scripts\python" "G:\Projetinhos\Patrimonio\notebooks\1- tratamento_acoes_mes.py"
echo Running Script 3
".venv\Scripts\python" "G:\Projetinhos\Patrimonio\notebooks\2- dinheiro_nubank_mensal.py"
echo Running Script 4
".venv\Scripts\python" "G:\Projetinhos\Patrimonio\notebooks\3- gastos.py"
echo Running Script 5
".venv\Scripts\python" "G:\Projetinhos\Patrimonio\load_data\load_data_gzip.py"

echo Press any key to activate the virtual environment and run Patrimonio.py using Streamlit
pause

call ".venv\Scripts\activate"
streamlit run "G:\Projetinhos\Patrimonio\Patrimonio.py"

echo Press any key to close this window
pause
