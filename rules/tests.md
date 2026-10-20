# Como escrever testes neste projeto

- pytest. Sem framework adicional.
- Regra de negócio é testada SEM banco, chamando o domínio direto.
  Se o teste precisa de SQLite para rodar, o desenho está errado (ADR-001).
- Um cenário por teste. Nada de teste que verifica cinco coisas.
- Nome: test__
  ex: test_saldo_ignora_lote_expirado
- Datas nos testes são explícitas e fixas. Nunca datetime.now().