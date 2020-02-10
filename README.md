### Нагрузочный тест для CPU и MYRIAD устройств.  

#### Подготовка  
Выполните установку [OpenVino toolskit](https://docs.openvinotoolkit.org). ([Installation guide](https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_linux.html))  
  
Для тестирования устройств MYRIAD:
* [руководство по конфигурации](https://docs.openvinotoolkit.org/latest/_docs_install_guides_installing_openvino_linux_ivad_vpu.html)  
* [руководство по конфигурации hddldaemon](https://www.google.ru/url?sa=t&rct=j&q=&esrc=s&source=web&cd=5&ved=2ahUKEwjK1veQ18bnAhUKEJoKHUAZDbcQFjAEegQIAxAB&url=https%3A%2F%2Fdls.ieiworld.com%2FIEIWEB%2FMARKETING_MATERIAL%2Fmustang%2Finitial_daemon_for_utilization_and_temperture_monitoring.pdf&usg=AOvVaw2BXkf228JHa2_WkdqhSdGc)

Выполните следующие команды:  
1. `cd [путь_к_папке_бенчмарка]/tools`  
2. `sh ./download_model.sh`  - выполняет скачивание файлов модели нейронной сети  
3. `sudo sh ./install_dependences.sh` - производит установку зависимостей, необходимых для работы бенчмарка  

#### Параметры запуска:  
Основные параметры тестирования прописываются в файле **benchmark.cfg**:  

| Параметр                  | Описание                                                                                            |
| ------------------------- |:-------------------------------------------------------------------------------------------| 
|`devices`                  | список устройств (доступные обозначения: CPU, MYRIAD).                                      |
|`save_logs_every_N_minutes`| период сохранения статистики в лог (указывается в **минутах**).                            |
|`running_time`             | время работы теста (указывается в **минутах**). При значении "-1" время работы бесконечно. |
|`path_to_cpu_extention`    | путь к файлу **libcpu_extension.so** (необходим для работы CPU плагина).                   |
|`path_to_hddl_daemon`      | путь к исполняемому файлу **hddldaemon** (необходим для сбора статистики устройств MYRIAD).| 
|`model_bin_name`           | название bin файла модели, на которой будет производиться инференс.                        |
|`model_xml_name`           | название xml файла модели, на которой будет производиться инференс.                        |
|`cpu_request_num`          | количество асинхронных запросов для CPU.                                                   |
|`myriad_request_num`       | количество асинхронных запросов для Myriad.                                                |

В процессе работы бенчмарка статистические данные о работе устройств будут сохраняться в подкаталоге папки **logs**. Имя подкаталога соответсвует дате и времени начала работы бенчмарка.  

#### Запуск теста  
Для запуска теста выполните команду `python3 run_benchmark.py`

#### Построение графиков по результатам теста
1. Откройте фалй **plotting.cfg**  
2. Параметру `actual_logs_dir` присвойте путь к папке с log-файлами. В папке должны содержаться подкаталоги CPU, MYRIAD, RAM (в зависимости от перечня устройств, для которых производилось тестирование)  
   *Присвоение значения производится через знак двоеточия!*
3. Выполните команду  `python3 plot_stats.py`
4. Построенные в результате работы программы графики будут находится в подкаталогах папки, указанной в файле **plotting.cfg**  