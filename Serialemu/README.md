# Serialemu

O programa serialemu emula um link serial com determinada taxa de bits, BER e atraso de propagação. Ele foi inicialmente desenvolvido para auxiliar no desenvolvimento de protocolos para comunicação por interfaces seriais, no escopo da disciplina Projeto de Protocolos da Engenharia de Telecomunicações do IFSC - Câmpus São José.

Para usá-lo, faça o seguinte:
1. Compile o serialemu. Este repositório foi gerado com o CLion, mas você pode compilá-lo com o programa cmake.
1. Execute-o de forma que ele apresente suas opções de execução:
   ```sh
   aluno@M2:~$ ./serialemu -h
   Uso: ./serialemu [-b BER][-a atraso][-f][-B taxa_bits] | -h

   BER: taxa de erro de bit, que deve estar no intervalo  [0,1]
   atraso: atraso de propagação, em milissegundos.
   taxa_bits: taxa de bits em bits/segundo
   -f: executa em primeiro plano (nao faz fork)
   ``` 
1. Execute-o então da forma desejada, selecionando a taxa de bits (default: ilimitada), BER (default: 0) e atraso de propagação (default: 0). O serialemu automaticamente vai para segundo plano (daemonize), liberando o terminal. Ex:
   ```sh
   aluno@M2:~$ ./serialemu -B 9600
   /dev/pts/17 /dev/pts/2
   aluno@M2:~$
   ```
   ... e anote os dois caminhos informados pelo serialemu: eles são as duas portas seriais que correspondem às pontas do link serial emulado.
1. Execute seu protocolo usando essas portas seriais virtuais.
