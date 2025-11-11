rem Ativa o venv "BigData", para evitar erros
cd BigData\Scripts
call activate.bat
cd ..
cd ..
rem Inicia o dashboard por meio do streamlit
streamlit run dashboard_trabalho.py
exit