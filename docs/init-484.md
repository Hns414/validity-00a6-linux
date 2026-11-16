# Resultado do discriminante e referência pública de 484 bytes

## Relato do participante

Em 2026-11-16, o participante enviou saída de terminal com atualização para `9d429de` (v0.16.0-research), 59 testes aprovados, compilação concluída e execução elevada de `--summarize-init-discriminator`:

```json
{"schema_version":4,"experiment":"E1","status":"reply_received_unvalidated","stage":"read","received_bytes":38,"biometric_support":false,"decode_status":"candidate_layout_unverified","discriminator_candidate":{"firmware_major":6,"flag_0x20_set":true,"derived_value":2},"full_selection_evaluated":false}
```

O [registro sanitizado](evidence/e1-discriminator-participant-report-2026-11-16.json) exclui prompt, nome de usuário/host, caminhos pessoais e texto do sudo. A operação real foi relatada pelo participante, não reproduzida pelo agente. Não foi recebido ou retido um dump da resposta.

## Consequência para as duas entradas

Sob o [layout candidato e predicado estático](init-discriminator.md), major 6 com bit 0x20 ativo deriva 2. A entrada 19 exige 3 e é excluída por esse filtro; a entrada 55 exige 2 e passa **por esse filtro**. Portanto, a correspondência anterior de versão/build com os 500 bytes de init_00 não basta e esse bloco não deve ser tratado como escolha demonstrada para o participante.

Os demais filtros do seletor, sua lógica de preferência e o contexto do transporte continuam pendentes. O resultado não significa seleção completa da entrada 55, envio de payload ou validação de biometria. O encoder offline de 500 bytes permanece uma demonstração restrita de montagem, sem uso no probe.

## Correspondência integral da entrada 55

Na DLL Dell de SHA-256 `6f1fd4db7057fc9b545e8e76df7f4975a6f69f22380dfb6f47bd78868a70e2a7`, o registro RVA 0x13d490 aponta para 484 bytes de argumentos. Uma leitura limitada ao intervalo mapeado da seção PE foi comparada à atribuição literal `init_hardcoded` no [blobs_90.py do python-validity fixado](https://github.com/uunicorn/python-validity/blob/a6bbc21dce7b8b3c3cd92378a0b2579a2fb45920/validitysensor/blobs_90.py).

O fonte público foi obtido por `git show` no commit fixado e analisado por AST com a ferramenta original de comparação; não foi importado ou executado. As comparações integrais em memória confirmaram:

- Os 484 argumentos são iguais ao bloco público de 485 bytes após remover seu opcode inicial.
- O byte 0x06 seguido dos 484 argumentos é exatamente igual ao bloco público completo.
- SHA-256 dos argumentos: `7071967a90f5a5ad82e206bdb5ab7aefdfb231cb106ea89dcbd11a64381f7bb1`.
- SHA-256 do frame de 485 bytes: `854b90943a8b865ca237b686112381d15460f715c88147ff6d83d7b8d264b1db`.

O [registro da comparação](evidence/init-484-public-comparison.json) publica somente metadados, hashes e resultados booleanos. Nenhum payload proprietário foi exportado para o repositório.

O nome de família “90” é localização da referência pública, não prova de que o 00a6 aceite o restante do protocolo do 0090. Identidade de bytes não decodifica operações internas, destino de memória ou persistência. Não executar o python-validity ou seu reset como consequência desta comparação.

## Validação e próximo trabalho

Esta etapa registra o relato e a comparação offline; não altera código executável. Os 59 testes e a compilação foram relatados pelo participante para v0.16 e já haviam passado no desenvolvimento. Não houve nova execução da suíte para estas alterações documentais.

Não é necessário repetir o teste. O próximo trabalho volta à análise dos filtros restantes e do caminho consumidor do bloco de 484 bytes, inclusive sua relação com os parâmetros diferentes do registro. Nenhum executor de inicialização foi habilitado.

## Reprodução por ferramenta

A [análise do fluxo público](public-init-flow.md) inclui agora um verificador offline original, limitado ao hash da DLL e ao commit público fixado. Ele reproduz a comparação sem exportar bytes; não habilita inicialização.
