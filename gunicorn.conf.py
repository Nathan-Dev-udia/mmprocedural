# Configuração lida sozinha pelo gunicorn no Render. O plano gratuito tem CPU lenta e montar um livro
# pode passar dos 30 s padrão; sem isso o worker é derrubado e o download falha.
timeout = 120
