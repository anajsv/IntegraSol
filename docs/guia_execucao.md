# Guia de execução do IntegraSol

Este guia reúne a preparação do ambiente, a execução local e um roteiro de utilização. Os comandos principais são para **Windows 11 com Python 3.12 de 64 bits**. A aplicação não exige compilação tradicional, Docker ou banco de dados.

## 1. Instalar o Python e extrair o projeto

Baixe o Python 3.12 pelo [site oficial](https://www.python.org/downloads/windows/). No instalador clássico, habilite o launcher `py` e a opção de adicionar o Python ao PATH, quando disponíveis. Depois, abra um novo terminal e confira:

```powershell
py -3.12 --version
```

Extraia o ZIP usando **Extrair Tudo**. Entre na pasta interna `IntegraSol`, onde estão `app.py`, `requirements.txt`, `calculo/` e `interface/`. Clique com o botão direito no fundo da pasta e escolha **Abrir no Terminal**. Não execute o projeto de dentro do ZIP.

## 2. Preparar o ambiente

Na pasta do projeto:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Esses comandos são necessários na primeira instalação em cada computador. A utilização direta de `python.exe` dispensa a ativação do ambiente e a alteração da política do PowerShell.

A instalação precisa de internet para baixar as dependências. Para reproduzir também as versões indiretas do ambiente registrado, pode-se instalar `requirements-lock.txt` em lugar de `requirements.txt`. Essa combinação foi verificada em Python 3.12/Linux; a conferência presencial em Windows permanece a confirmar.

## 3. Abrir e encerrar a aplicação

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abra **http://localhost:8501** se o navegador não abrir automaticamente. Mantenha o terminal aberto durante o uso. Para encerrar o servidor, pressione **Ctrl+C**; fechar somente a aba do navegador não encerra o programa.

Nas próximas utilizações, basta entrar na mesma pasta e repetir o comando de abertura. Não é necessário reinstalar os pacotes. A execução não consulta APIs externas nem baixa dados de terceiros.

## 4. Utilizar o protótipo

1. Clique em **Calcular** para executar o exemplo inicial: R=2 m, densidade=1 kg/m³ e n=40.
2. Consulte volume, massa, centro e erro. A configuração correspondente aparece junto dos resultados.
3. Gire a esfera e ajuste i, j, k para consultar a célula destacada. A caixa laranja representa a célula inteira.
4. Abra a explicação matemática e compare as resoluções 10, 20 e 40 na tabela.
5. Ao alterar um parâmetro, clique novamente em **Calcular**. Até isso ocorrer, o resultado anterior permanece identificado.

O botão **Restaurar exemplo** repõe os parâmetros iniciais e calcula novamente. A inspeção de células e a opção de ocultar pontos não refazem a integral.

### Roteiro curto de demonstração

| Ação | O que observar |
|---|---|
| Calcular o exemplo inicial | Volume de 33,552000 m³ e erro de aproximadamente 0,124375% |
| Selecionar (20,20,20) | Ponto médio (0,05; 0,05; 0,05) m; peso de 0,001 m³ |
| Selecionar (0,0,0) | Ponto fora da esfera; peso e contribuição de massa nulos |
| Alterar a densidade para 2 e calcular | Massa de 67,104000 kg; volume preservado |
| Consultar o refinamento | Mesmos parâmetros físicos, com resoluções diferentes |

## 5. Executar os testes

Na pasta do projeto:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

A execução já registrada aprovou **50 testes**. A saída está em [execucao-testes.txt](execucao-testes.txt); os valores numéricos estão em [resultados_verificados.json](resultados_verificados.json). A atualização destes guias não representa uma nova execução dos testes.

## 6. Resolver problemas comuns

| Problema | Como resolver |
|---|---|
| `py` não reconhecido | Confira a instalação do Python e do launcher; reabra o terminal. Se `python --version` indicar 3.12, use `python -m venv .venv`. |
| Python 3.12 não encontrado | Instale essa versão. O comando `py -0p` lista os interpretadores disponíveis. |
| `app.py` ou `requirements.txt` não encontrado | Entre na pasta interna `IntegraSol`, após extrair o ZIP. |
| `ModuleNotFoundError` | Instale e execute usando o mesmo `.venv\Scripts\python.exe` dos comandos acima. |
| Bloqueio de `Activate.ps1` | Não é necessário ativar o ambiente; use diretamente o executável da `.venv`. |
| Porta 8501 em uso | Pare a execução anterior ou acrescente `--server.port 8502` ao comando de abertura e use http://localhost:8502. |
| Cena 3D não aparece | Use navegador atualizado com suporte a WebGL e confira a aceleração gráfica. |
| Resultado não mudou após alterar um controle | Clique em Calcular; o aviso identifica os parâmetros pendentes. |

## 7. Executar em outro computador

Copie e extraia o ZIP, instale o Python e crie um novo ambiente virtual com os mesmos comandos. Não copie a pasta `.venv` entre computadores.

Em Linux/macOS com Python 3.12 disponível:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Para entender as fórmulas, os módulos e os limites da versão, consulte o [guia técnico](guia_tecnico.md). O histórico permanece no [registro de atividades](Registros_Desenvolvimento_IntegraSol.docx).
