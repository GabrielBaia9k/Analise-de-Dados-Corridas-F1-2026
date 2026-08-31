Um dashboard interativo em desenvolvimento para a temporada de 2026 de Formula 1, este trabalho é feito por um fan e não possui relação oficial nenhuma com a Formula 1.
Pode ser executado tanto localmente quanto hosteado em um serviço de dashboard online.

repositório para atualizar a tabela: https://github.com/toUpperCase78/formula1-datasets (licença GPLv4)

repositório com os layouts de circuitos: https://github.com/julesr0y/f1-circuits-svg?tab=CC-BY-4.0-1-ov-file (licença CC-BY-4.0)

Antes de rodar leia requirements.txt para instalar os pacotes necessários

Rode em localhost no powershell com: shiny run --reload main.py

Para fazer o deploy em shinyapps.io: rsconnect deploy shiny . --name "accountname" --title "dash-f1"

acesse online em: kadran9k.shinyapps.io/dash-f11/
