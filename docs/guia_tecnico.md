# Guia técnico do IntegraSol

Para instalar e abrir a aplicação, consulte o [guia de execução](guia_execucao.md). Este documento concentra o método matemático, a organização do código e a validação.

## Método e escopo

A região é a esfera **x²+y²+z² ≤ R²**, discretizada na caixa [-R,R]³. O protótipo usa densidade constante positiva e n=10, 20 ou 40 subdivisões por eixo.

- Passos: Δx=Δy=Δz=2R/n.
- Pontos médios: xᵢ=-R+(i+1/2)Δx, com expressões análogas para y e z.
- Jacobiano cartesiano: J=1.
- Peso: wᵢⱼₖ=χE(xᵢ,yⱼ,zₖ)ΔxΔyΔz; o indicador vale zero fora da esfera.
- Volume: Vₙ=Σw. Parcela de massa: Δm=ρ₀w. Massa: Mₙ=ΣΔm.
- Momentos: Qx=ΣxΔm, Qy=ΣyΔm, Qz=ΣzΔm.
- Centro: Cₙ=(Qx/Mₙ,Qy/Mₙ,Qz/Mₙ).

As somas usam float64. As células de fronteira são aceitas ou rejeitadas pelo ponto médio, sem recorte geométrico. Comprimentos estão em m; volume em m³; densidade em kg/m³; massa em kg; primeiros momentos em kg·m.

## Código e dados

| Módulo | Funções e responsabilidade |
|---|---|
| `calculo/geometria.py` | Validar raio, definir limites e testar pertencimento |
| `calculo/coordenadas.py` | Explicitar J=1 e o elemento de volume |
| `calculo/integracao.py` | Gerar pontos, pesos e parcelas; somar grandezas e consultar células |
| `calculo/validacao.py` | Referências independentes, erros e refinamento |
| `interface/componentes.py` | Controles, resultados, inspetor e explicações |
| `interface/visualizacao.py` | Superfície ilustrativa, pontos reais, célula e centro |
| `app.py` | Coordenar chamadas e preservar a execução no estado da sessão |

`integrar_esfera(raio, densidade, resolucao)` retorna um dicionário com `parametros`, `grandezas`, `discretizacao` e `estatisticas`. Os pontos têm forma `(n,n,n,3)` e os pesos, contribuições e máscara, `(n,n,n)`. A consulta usa índices [i,j,k], começando em zero. Não há dependência de Streamlit ou Plotly em `calculo/`.

O botão Calcular atualiza o resultado e o refinamento. A inspeção lê os arrays guardados sem integrar novamente. A seleção visual é determinística e inclui a amostra selecionada, respeitando o limite de 3.000 pontos médios. Ela não modifica as somas.

## Validação registrada

Referências: Vref=4πR³/3, Mref=ρ₀Vref e Cref=(0,0,0). O erro relativo de volume/massa é |valor-referência|/|referência|; a interface exibe porcentagem. Para o centro, usam-se erro absoluto e normalização por R, pois a referência é zero.

Para R=2 m e ρ₀=1 kg/m³, Vref≈33,51032164 m³:

| n | Candidatos | Aceitos | Volume (m³) | Erro (%) |
|---:|---:|---:|---:|---:|
| 10 | 1.000 | 552 | 35,328000 | 5,424234 |
| 20 | 8.000 | 4.224 | 33,792000 | 0,840572 |
| 40 | 64.000 | 33.552 | 33,552000 | 0,124375 |

A execução existente registra **50 testes aprovados**, cobrindo entradas, grade, pesos, somas, escala do raio/densidade, inspeção, limite visual e estado da interface. Em n=40, o erro de volume é inferior a 1%; o centro apresenta resíduos da ordem de 10⁻¹⁶ m. Os valores correspondem à execução registrada em 27/10/2026; a atualização dos guias não representa uma nova execução dos testes.

Ambiente verificado: Python 3.12.14/Linux; NumPy 2.3.5, Streamlit 1.51.0, Plotly 6.5.0 e pytest 8.4.2. As versões estão fixadas em `requirements.txt`; `requirements-lock.txt` registra também as dependências indiretas. A saída dos testes e os resultados completos permanecem nesta pasta.

## Limites e registro de atividades

São contemplados somente esfera cartesiana na origem, densidade constante e resolução máxima 40. Outros sólidos, densidade variável, sistemas curvilíneos, CAD/STL e gráfico adicional de convergência ficam fora do protótipo. O erro da fronteira não tem redução monotônica garantida em qualquer sequência de resoluções.

O [registro de atividades](Registros_Desenvolvimento_IntegraSol.docx) é a referência para a cronologia e as decisões; preserva as ressalvas sobre o histórico simulado. A implementação está concluída no escopo descrito. A instalação nas duas máquinas e a conferência visual WebGL permanecem a confirmar; o servidor e o AppTest foram verificados no ambiente registrado.

## Referências essenciais

Plano de trabalho do IntegraSol e registro de atividades fornecidos pelos autores. Documentação oficial consultada na construção: [Python](https://docs.python.org/3.12/library/venv.html), [NumPy](https://numpy.org/doc/stable/reference/generated/numpy.meshgrid.html), [Streamlit](https://docs.streamlit.io/1.51.0/develop/api-reference/charts/st.plotly_chart), [Plotly](https://plotly.com/python/3d-surface-plots/) e [pytest](https://docs.pytest.org/en/stable/how-to/parametrize.html).
