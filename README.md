### Нагрузочный тест для CPU и MYRIAD девайсов.  

#### Подготовка  
Выполните следующие команды:  
1. `cd [путь_к_папке_бенчмарка]/tools`  
2. `sh ./download_model.sh`  - выполняет скачивание файлов модели нейронной сети  
3. `sudo sh ./install_dependences.sh` - производит установку зависимостей, необходимых для работы бенчмарка  

#### Параметры запуска:  
Основные параметры тестирования прописываются в файле **benchmark.cfg**:  

| Параметр                  | Описание                                                                                            |
| ------------------------- |:-------------------------------------------------------------------------------------------| 
|`devices`                  | список девайсов (доступные обозначения: CPU, MYRIAD).                                      |
|`save_logs_every_N_minutes`| период сохранения статистики в лог (указывается в **минутах**).                            |
|`running_time`             | время работы теста (указывается в **минутах**). При значении "-1" время работы бесконечно. |
|`path_to_cpu_extention`    | путь к файлу **libcpu_extension.so** (необходим для работы CPU плагина).                   |
|`path_to_hddl_daemon`      | путь к исполняемому файлу **hddldaemon** (необходим для сбора статистики устройств MYRIAD).| 
|`model_bin_name`           | назавние bin файла модели, на которой бужет производиться инференс.                        |
|`model_xml_name`           | назавние xml файла модели, на которой бужет производиться инференс.                        |
|`cpu_request_num`          | количество асинхронных запросов для CPU.                                                   |
|`myriad_request_num`       | количество асинхронных запросов для Myriad.                                                |

#### Запуск теста  
Для запуска теста выполните команду `python3 run_benchmark.py`

#### Построение графиков по результатам теста
1. Откройте фалй **plotting.cfg**  
2. Параметру `actual_logs_dir` присвойте путь к папке с log-файлами. В папке должны содержаться подкаталоги CPU, MYRIAD, RAM (в зависимости от перечня устройств, для которых производилось тестирование)  
   **Присвоение значения производится через знак двоеточия!**
3. Выполните команду  `python3 plot_stats.py`
4. Построенные в результате работы программы графики будут находится в подкаталогах папки, указанной в файле **plotting.cfg**  