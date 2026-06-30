# Pipeline de Automação CAD

Este projeto executa automaticamente a preparação de geometrias CAD para análise, seguindo as etapas:

1. Importação do arquivo STEP.
2. Classificação dos componentes utilizando Machine Learning.
3. Renomeação conforme a classe prevista.
4. Busca de componentes equivalentes em banco de dados.
5. Substituição automática por peças padronizadas.
6. Limpeza geométrica das peças.
7. Reconstrução de tubos e perfis abertos.
8. Identificação de componentes soldados.
9. Criação das soldas correspondentes.
10. Organização dos nomes e espessuras.
11. Exportação para formato XT.
12. Inicialização do HyperMesh.
