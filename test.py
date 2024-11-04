import subprocess
import time

# Configurações
ssd_test_cases = [
    ("Padrão", "python3 testcp.py"),
    ("Sem integridade", "./venv/bin/python3 masscopy.py test_files test_output -v y -e y -i n"),
    ("Sem integridade (Detailed)", "./venv/bin/python3 masscopy.py test_files test_output -v y -e y -i n -m detailed"),
    ("Com integridade", "./venv/bin/python3 masscopy.py test_files test_output -v y -e y -i y"),
    ("Com integridade (Detailed)", "./venv/bin/python3 masscopy.py test_files test_output -v y -e y -i y -m detailed")
]

ssd_chunk_sizes = {
    "64 MB": 67108864,
    "128 MB": 134217728,
    "256 MB": 268435456,
    "512 MB": 536870912,
}

hdd_test_cases = ssd_test_cases
hdd_chunk_sizes = ssd_chunk_sizes

output_file = "resultado_teste.txt"

def run_test(description, command):
    print(f"Executando: {description}")
    start_time = time.time()
    subprocess.run(command, shell=True)
    elapsed_time = time.time() - start_time
    return elapsed_time

def write_results(drive_type, test_cases, chunk_sizes, output_file):
    with open(output_file, "a") as file:
        file.write(f"\n{drive_type}\n\n")
        file.write("cp -r\n")

        # Teste cp padrão
        cp_time = run_test("Padrão - cp", test_cases[0][1])
        file.write(f"{test_cases[0][0]} - {cp_time:.2f}s\n")

        # Testes com `masscopy.py` em diferentes tamanhos de chunk
        for chunk_desc, chunk_size in chunk_sizes.items():
            for test_name, test_cmd in test_cases[1:]:
                cmd = f"{test_cmd} -c {chunk_size}"
                time_taken = run_test(f"{test_name} - {chunk_desc}", cmd)
                file.write(f"{chunk_desc} - {test_name} - {time_taken:.2f}s {cmd}\n")
            file.write("\n")


# Executa testes e escreve os resultados no arquivo
write_results("Test", ssd_test_cases, ssd_chunk_sizes, output_file)

print(f"Testes concluídos. Resultados salvos em '{output_file}'")
