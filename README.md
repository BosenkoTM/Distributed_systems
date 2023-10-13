# Lecturer
Timur Bosenko M. (bosenkotm@mgpu.ru)

Здесь Вы можете найти все материалы по лекциям **`Распределенные системы`**.

Дисциплина нацелена на изучение принципов и технологий распределенных вычислений, знакомство с различными классами распределенных систем и получение практических навыков разработки распределенных приложений.По завершению лекционномого модуля, рассмотрим наиболее распространенное программное обеспечение и фреймворки.

## Программное обеспечение 
   
 `УДАЛЕННОЕ РАБОЧЕЕ МЕСТО`:
   
 - OC **`Ubuntu 20.04`** на базе кластера **`МГПУ`**. Номер РМ студента получить у ведущего лектора. Для работы потребуется клиент [anydesk](  https://anydesk.com/en/downloads/windows).
   
 `ВИРТУАЛЬНАЯ ГОСТЕВАЯ ОС`:
 
 - `D_System_22` [vm - VirtualBox](https://disk.yandex.ru/d/RTZvbDhtfXInMg), в его комплект входит:
    - `VirtualBox-6.1.30-148432-Win.exe` - ПО для разворачивания виртуальной ОС; 
    - `St_work_1.ova` - образ настроенной ОС `Ubuntu 18.04`;
    - `St_work_Hadoop.ova` - образ настроенной ОС `Ubuntu 18.04 + Hadoop`;
    - `login.txt`;
    - `ubuntu-18.04.6-desktop-amd64.iso` - исходный образ ОС.
    
## Темы курсовых проектов
   [АДЭУ-211](https://docs.google.com/spreadsheets/d/1vH9CPcBrWd2rGgXVlzg4eaXm8DNor1-3s4Um11_e2hA/edit?usp=sharing)

   Распределение студентов КР:
[АДЭУ-211](/kp/УтвКП_АДЭУ-211-2023.pdf)
   
   | ФИО  | Дата представления КП |
| --------------| :---: |
|   | 01.12.2023    |

   
   ### Регламент написания и защиты курсового проекта.

При защите курсового проекта оцениваются:
- соответствие содержания курсового проекта ее теме;

- полнота и глубина разработки согласно поставленным задачам и цели работы;

- актуальность и новизна;

- степень проработанности литературных источников;

- использование вычислительной и экспериментальной техники при проведении исследований;

- степень самостоятельности при выполнении работы;

- содержание доклада и ответы на вопросы.

[Методические рекомендации к выполнению курсового проекта](https://disk.yandex.ru/i/6_ypM5IRQTfpBA)

[Пример-2023](https://disk.yandex.ru/d/p31hgz487lPzzQ)
## Текущая успеваемость
 [АДЭУ-201](https://docs.google.com/spreadsheets/d/1NOTUaM9YFTO9QEV7WKDY1KJoWyKj5iSkfVdgChCiw_o/edit?usp=sharing)

 [АДЭУ-211](https://docs.google.com/spreadsheets/d/1rwdG4OYKxMX2NpclxNVn-L5Y_67TCcN1Y9awgpJACAA/edit?usp=sharing)

## Вопросы к экзамену

- [2023-2024](/examp_ds_2022_2023.pdf)

## Билеты(зачет)

- [2023-2024](/examp2022/Билеты%20экзамен%20Распределенные%20системы%20ТП-191.pdf)

## Distributed_systems

- `01-ЛЕКЦИЯ` [Введение](lectures/1-intro.pdf)

- `02-ЛЕКЦИЯ` [Взаимодействие в распределенных системах](/lectures/02-ЛЕКЦИЯ_Взаимодействие%20между.pdf)

- `03-ЛЕКЦИЯ` [HTTP и веб-сервисы](/lectures/03-ЛЕКЦИЯ_HTTP%20и%20веб-сервисы.pdf)

- `04-ЛЕКЦИЯ` [Групповые взаимодействия](lectures//lectures/04-ЛЕКЦИЯ_Групповые%20взаимодействия.pdf)

- `05-ЛЕКЦИЯ` [Непрямое взаимодействие](/lectures/05-ЛЕКЦИЯ_Непрямое%20взаимодействие.pdf)
   - `05-01-ЛЕКЦИЯ` [docker-indirect](/lectures/05-01-docker-indirect-comm.pdf)
   - `05-02-ЛЕКЦИЯ` [Требования к распределенных систем, моделям данных и доступа](/lectures/05-02-Requirements_for_DS.pdf)
   - `05-03-ЛЕКЦИЯ` [Непрямое взаимодействие](/lectures/05-0-lecture_Kafka_intro.pdf)
- `06-ЛЕКЦИЯ` [Обнаружение отказов](/lectures/06-ЛЕКЦИЯ_Обнаружение%20отказов.pdf)

- `07-ЛЕКЦИЯ` [Именование и поиск](lectures/)

- `08-ЛЕКЦИЯ` [Масштабирование](lectures/)

- `09-ЛЕКЦИЯ` [Параллельная обработка](lectures/)

- `10-ЛЕКЦИЯ` [Репликация данных](lectures/)

## Практические работы задания
- [practice](https://github.com/BosenkoTM/Distributed_systems/tree/main/seminars).

## Индивидуальные задания 
- [d-zadanie](https://github.com/BosenkoTM/Distributed_systems/tree/main/d-zadanie ).

## Семинары(доп)

- `Семинар 1`. [Протокол HTTP/HTTPS](practice/S-1-%20HTTP)
 
- `Семинар 2`.

- [Multicast](d-zadanie/04-multicast) (Выполнить на базе кластера `МГПУ`).

- [Расчет конфигурации сети Ethernet](https://disk.yandex.ru/i/WSwJSNc6PP3aRg).

- [Расчет IPv4-подсетей](https://disk.yandex.ru/i/Bnn0pAECM3T2Mg).
  
- [Работа с адресами IP сетей](https://disk.yandex.ru/i/huaNfC05bwGgxQ).

- `Семинар 3`. [Message queue, RabbitMQ.](/d-zadanie/03-mq) (Выполнить на базе кластера `МГПУ`).

- `Семинар 4`. [Детектор отказов](https://github.com/BosenkoTM/Distributed_systems/tree/main/d-zadanie/06-failure_detection#%D1%81%D0%B5%D0%BC%D0%B8%D0%BD%D0%B0%D1%80-6-group-membership-%D0%B8-%D0%B4%D0%B5%D1%82%D0%B5%D0%BA%D1%82%D0%BE%D1%80-%D0%BE%D1%82%D0%BA%D0%B0%D0%B7%D0%BE%D0%B2).

- `Семинар 5`. [Kafka.](https://github.com/BosenkoTM/kafka),  [Kafka2.](https://github.com/Zabi82/KafkaLab) [Kafka3.](https://github.com/cblanton45/kafka-labs).

- `Семинар 6`. 
   
   - [Парадигма Map Reduce - Преподаватель](practice/S-2-09-map-reduce)
   
   - [Парадигма Map Reduce - Студент]()

- `Семинар 7`. [01_HADOOP администрирование](https://github.com/BosenkoTM/ds_practice/tree/main/exercises/winter_semester_2021-2022/05_hadoop)
  - Решение самостоятельного задания `Семинар 7` [тут](https://github.com/BosenkoTM/ds_practice/tree/main/solutions/winter_semester_2021-2022/05_hadoop)
  - [02_HADOOP сам_задание](/practice/S-3-HADOOP/2.%20Hadoop%20Lab-1.pdf)
  
- `Семинар 8`. [Репликация данных](practice/S-4-10-replication/pr_replica_single_server.pdf)
  - [Предварительное создание БД](/practice/S-4-10-replication/db_creator.pdf)
   

## ТЕСТ 1. Распределенные системы.  

`06.10.2023 09-10`

[ССЫЛКА ДЛЯ ВХОДА](https://docs.google.com/forms/d/e/1FAIpQLScEjZmp_Fsx2qGEp-KWWR5L8UfUrZs0GmGJIM_Nd3I0nzbuwg/viewform?embedded=true)

- Темы тестирования: Понятие распределенных информационных систем, Основные принципы технологии  «клиент-сервер», 
Модели взаимодействия компонентов РС, Распределенная обработка данных. 
`Глава 1` - `Глава 2` Учебник [Бабичев С. Л](https://urait.ru/book/raspredelennye-sistemy-445188)

## ТЕСТ 2. Распределенные системы. 
`24.11.2023`

[ССЫЛКА ДЛЯ ВХОДА](https://docs.google.com/forms/d/e/1FAIpQLScx-U2XsIRvTkMHWHqbu15K9I9lNxc-n2NCgK-PiC22B0BTzA/viewform?embedded=true)

- Темы тестирования:  `Глава 9.` Архитектура распределенных систем. + конспект
Учебник [Бабичев С. Л](https://urait.ru/book/raspredelennye-sistemy-445188)
- [Конспект лекций](Lectures/help_test2.pdf)

## Дополнительные материалы
- [Основные понятия Docker](/Lectures/05-01-docker-indirect-comm.pdf) 
- [Docker help](/Lectures/docker_help.pdf) 

### Основная литература

1.	Бабичев, Сергей Леонидович. Распределенные системы [Электронный ресурс]: учеб. пособие для вузов / С. Л. Бабичев, К. А. Коньков. – М. : Юрайт, 2020. https://urait.ru/book/raspredelennye-sistemy-457005 

2.	Распределенные системы: учебное пособие для студентов, обучающихся по направлению подготовки 38.03.05 Бизнес-информатика / [авт.-сост. А.В. Демина, О.Н. Алексенцева]. 2018. – 108 с. 

3.	Клеппман М.Высоконагруженные приложения. Программирование, масштабирование, поддержка. — СПб.: Питер, 2018 — 640 с.

### Дополнительная литература

4.	Austin Parker Distributed Tracing in Practice Instrumenting, Analyzing, and Debugging Microservices, y O’Reilly Media, Inc., 2020
5.	Sigismondo Boschi RabbitMQ Cookbook Packt Publishing 2013
6.	Burns, B. (2018). Designing Distributed Systems : Patterns and Paradigms for Scalable, Reliable Services (Vol. First edition). Sebastopol, CA: O’Reilly Media. Retrieved from http://search.ebscohost.com/login.aspx?direct=true&site=eds-live&db=edsebk&AN=1713745
7.	Kleppmann, M. (2017). Designing Data-Intensive Applications : The Big Ideas Behind Reliable, Scalable, and Maintainable Systems. Sebastopol, CA: O’Reilly Media. Retrieved from http://search.ebscohost.com/login.aspx?direct=true&site=eds-live&db=edsebk&AN=1487643
8. Petrov, A., & O’Reilly for Higher Education (Firm). (2019).
8. Database Internals : A Deep Dive Into How Distributed Data Systems Work (Vol. First edition). Sebastopol, CA: O’Reilly Media. Retrieved from http://search.ebscohost.com/login.aspx?direct=true&site=eds-live&db=edsebk&AN=2250514

