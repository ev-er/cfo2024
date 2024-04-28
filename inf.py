import time

import pandas as pd
import numpy as np
import torch
import bert_dataset
import bert_classifier
import os.path


MODEL_PATH = './bert.pt'

torch.set_warn_always(False)

answer_class = {0: 'После успешного прохождения выпускных испытаний вы получите документ, подтверждающий уровень ваших компетенций. Подробнее - https://gb.ru/academiccertificates',
  1: 'Чтобы получить итоговый документ, нужно сдать итоговую и все промежуточные аттестации. По их результатам оцениваются компетенции, которые важны для итогового документа.',
  2: 'Можем его выдать, если вы:\n\nоплатили обучение после 3 декабря 2019 года;\nимеете среднее или высшее профессиональное образование — подойдут диплом СПО или ВО. Если вы ещё не закончили СУЗ или ВУЗ, подойдёт справка из образовательного учреждения;\nпри зачислении предоставили пакет документов — паспорт, диплом, СНИЛС, сведения о смене ФИО (при наличии), сведения о признании иностранного диплома (при наличии);\nсдали все промежуточные аттестации до даты итоговой аттестации;\nуспешно сдали итоговую аттестацию.\nИтоговой аттестацией может быть:\n\nитоговый экзамен;\nзащита проекта;\nдругие формы итоговой аттестационной работы.\nМы подготовим диплом в течение 30 дней от даты итоговой аттестации. Чтобы его получить, обратитесь к куратору.',
  3: 'Можем его выдать, если вы:\n\nоплатили обучение после 3 декабря 2019 года;\nимеете среднее или высшее профессиональное образование — подойдут диплом СПО или ВО. Если вы ещё не закончили СУЗ или ВУЗ, подойдёт справка из образовательного учреждения;\nпри зачислении предоставили пакет документов — паспорт, диплом, СНИЛС, сведения о смене ФИО (при наличии), сведения о признании иностранного диплома (при наличии);\nсдали все промежуточные аттестации до даты итоговой аттестации;\nуспешно сдали итоговую аттестацию.\nИтоговой аттестацией может быть:\n\nтестирование по всем темам программы;\nзащита индивидуального проекта, итоговой работы или портфолио;\nзащита командного проекта;\nдругие виды итоговых испытаний.\nМы подготовим удостоверение в течение 30 дней от даты итоговой аттестации. Чтобы получить его, обратитесь к куратору.',
  4: 'Диплом или удостоверение отправим бесплатно Почтой России.',
  5: 'Обычно уроки проходят на одной из платформ — Zoom или livedigital.',
  6: 'Курсы проходят в порядке, указанном в разделе «Моё обучение». Расписание для них будет появляться постепенно.',
  7: 'Мы используем разные форматы обучения. Вас ждут лекции и практикумы, групповые занятия и индивидуальные консультации, вебинары и записанные уроки, интервью с предпринимателями и учёными. В процессе обучения вы столкнётесь с несколькими видами курсов:\n\nВидеокурсы с предзаписанными видео, которые вы можете посмотреть в любое время. Чаще всего это подготовительные и вводные курсы, а также курсы от нашей команды. Например: «\u200eКурс компьютерной грамотности», «Центр карьеры GeekBrains: как мы помогаем студентам в поиске работы» и «\u200eИтоговые документы об обучении — старт учёбы».\nВ таких курсах нет домашних заданий, за которые вы получите оценку, но иногда есть задания для самопроверки и закрепления материала.\n\nВебинарные курсы с онлайн-уроками по расписанию. Если вы не смогли прийти на вебинар, сможете посмотреть его в записи. После урока нужно выполнить домашнее задание, чтобы закрепить материал. Преподаватель или ревьюер проверит работу и поставит за неё оценку. Иногда на таких курсах есть наставник, которому можно задать вопрос по программе.\n\nКурсы смешанного формата включают в себя видеоуроки и вебинары, разные практические задания — для оценки и для самопроверки. Как и на вебинарных курсах, работы проверяет преподаватель или ревьюер.',
  8: 'Сейчас в GeekBrains около 40 форматов занятий. Самые популярные: лекции, семинары, практикумы и консультации. Вы можете встретить не все — форматы зависят от программы курса.\n\nЛекции — теоретический блок. Преподаватель рассказывает теорию и показывает примеры. Занятия проходят по расписанию, в формате вебинара или в записи.\n\nСеминары — практический блок. Преподаватель делает упор на прикладные знания, помогает закрепить теорию практикой, отвечает на вопросы студентов. Занятия проходят по расписанию в формате вебинара, но их можно пересмотреть в записи. Советуем заниматься очно, чтобы не копить вопросы.\n\nПрактикумы — занятия для ответов на вопросы. Обычно их проводят после сложных тем. Например, на «Разработчике» практикумы есть после курсов «Введение в контроль версий» и «Знакомство с языками программирования». Занятия идут по расписанию в формате вебинара.\n\nКонсультации — индивидуальные занятия преподавателя со студентом. Вы можете попросить о консультации, если у вас набралось много вопросов, хотите подтянуть или углубить знания в какой-то теме. Это дополнительная возможность за рамками основной программы. Она оплачивается отдельно.',
  9: 'Если вы не смогли присутствовать на вебинаре, посмотрите его в записи. Видео появится на странице урока в течение суток после его окончания.',
  10: 'Задания, которые требуют проверки, оценивает преподаватель или ревьюер. За работу вы можете получить:\n\n«отлично»\n«хорошо»\n«удовлетворительно»\n«не принято»\nЕсли преподаватель поставил «не принято», вы можете пересдать работу. На странице с практическим заданием автоматически откроется возможность прикрепить новый файл или ссылку. Там же будет указан новый дедлайн. Если вы не успеете прикрепить работу в новый срок, пересдать её больше не получится, а оценка останется прежней — «не принято».',
  11: 'Мы можем перевести вас в другую группу в рамках срока обучения и дополнительных 6 месяцев сверху. Срок обучения отсчитывается с даты оплаты обучения.\nКоличество переводов зависит от срока программы:\n\nЕсли ваш продукт предусматривает возможность выбора специализации:\n12 месяцев — 1 перевод на каждый блок обучения, суммарно 3 перевода на весь срок обучения.\n24 месяца — 1 перевод на каждый блок обучения, суммарно 4 перевода на весь срок обучения.\n36 месяцев — 1 перевод на каждый блок обучения, суммарно 4 перевода на весь срок обучения.\nЕсли ваш продукт не предусматривает возможность выбора специализации:\n6 месяцев — 1 перевод на все время обучения.\n9 месяцев — 1 перевод на все время обучения.\n12 месяцев — 2 перевода на все время обучения.\nУзнать о сроках обучения и специализациях можно из программы обучения на странице вашего продукта.',
  12: 'Задание найдёте внутри курса, во вкладке «Практическое задание». Там же сможете сдать работу. Сделать это можно несколькими способами:\n\n- перейти по ссылке и решить задачу, если это задание с автоматической проверкой кода;\n- прикрепить файл с выполненным заданием — нажать на зелёную кнопку «Загрузить практическое задание»;\n- если делали работу в git или гугл-документе, прикрепить ссылку на него в поле «\u200eКомментарий к практическому заданию». Не забудьте открыть доступ к документу, чтобы эксперт смог сразу приступить к проверке.',
  13: 'Длительность программы зависит от пакета обучения:\n\nСпециалист — 6 или 9 месяцев — зависит от технологической специализации, уровень Junior.\nСпециалист с опытом — 6 месяцев. Опция для тех, у кого уже есть базовые знания или опыт в IT.\nИнженер — 12 месяцев, уровень Junior.\nМастер — 24 месяца, уровень Middle.\nПро — 36 месяцев, уровень Middle+.',
  14: 'Вкладка ЛК - Моё обучение. Здесь находятся все курсы, которые вам доступны. Они объединены в несколько разделов — Основное обучение, Отдельные курсы, Буткемп, Карьера, Наставничество.',
  15: 'Подготовка — курсы, которые помогут подготовиться к основной программе;\n\nАктивные — курсы, которые идут сейчас;\n\nЧетверти — основные курсы программы. Расписание для них появится автоматически, если вы записаны в группу.',
  16: 'Здесь находятся курсы, которые не входят в программу обучения. Например, «GeekSpeak» — тематические онлайн-лекции от экспертов. Вы можете проходить их по желанию.',
  17: 'На странице профиля нажмите «Редактировать профиль» и откройте вкладку «\u200eУведомления». Чтобы включить или выключить уведомления, переключите тумблер. Если хотите получать сообщения только о некоторых событиях, отметьте их галочкой.',
  18: 'На странице профиля нажмите «Редактировать профиль».\n\nВы можете указать ФИО, дату рождения, интересы, email и телефон, рассказать о себе. Мы советуем также указать город и часовой пояс, это нужно для корректной работы календаря.\n\nЧтобы подтвердить номер телефона, введите его в поле «Телефон для авторизации», нажмите «\u200eСохранить», а затем — «\u200eПодтвердить телефон».\n\nУдалить аккаунт можно на этой же странице.',
  19: 'Основной блок, где вы получите базовые навыки, которые нужны, чтобы освоить профессию.\nСпециализация — интересная вам специальность, на которой вы сфокусируетесь.\nТехнологическая специализация — узкопрофильный технологический путь в рамках специализации.',
  20: 'Программы профессиональной переподготовки направлены на освоение знаний и навыков в новой для вас сфере. Например, если вы занимаетесь менеджментом, но хотите научиться программировать.\n\nПрограммы повышения квалификации направлены на совершенствование и получение новых навыков в сфере, в которой у вас уже есть квалификация. Например, если вы копирайтер, но хотите стать редактором.',
  21: 'Расписание каникул на 2024:\n\n26 декабря 2023 — 8 января 2024\n29 апреля — 14 мая\n7 августа — 20 августа\n30 октября — 12 ноября',
  22: 'Расписание вебинаров зависит от группы, в которой вы учитесь. Проверить расписание можно в календаре на gb.ru — там отобразятся все уже запланированные уроки.',
  23: 'Специализация «Программист»\nWindows\n\nОС Windows 10 или выше\nПроцессор 2.30 ГГц или быстрее\nВидеокарта 2 Гб видеопамяти\nОперативная память 8+ Гб или больше\nСвободное место на жёстком диске 20 Гб и больше\nmacOS\n\nОС macOS 10.13 или выше\nПроцессор 2.0 ГГц или быстрее\nОперативная память 8+ Гб или больше\nВидеокарта 1 Гб видеопамяти\nСвободное место на жёстком диске 10 Гб и больше',
  24: 'Специализация «Тестировщик»\nWindows\n\nОС Windows 10 или выше\nПроцессор 2.30 ГГц или быстрее\nВидеокарта 4 Гб видеопамяти\nОперативная память 8+ Гб или больше\nСвободное место на жёстком диске 30 Гб и больше\nmacOS\n\nОС macOS Catalina (версия 10.15) или выше\nПроцессор 2.0 ГГц или быстрее\nОперативная память 8+ Гб или больше\nВидеокарта 2 Гб видеопамяти\nСвободное место на жёстком диске 40 Гб и больше',
  25: 'Мы помогаем нашим выпускникам найти работу. Как мы это делаем, можно узнать здесь - https://gb.ru/employmentassistance',
  26: 'Вы можете обратиться за помощью в поиске работы в центр карьеры после завершения обучения по основной программе.\n\nПосле сдачи итоговой аттестации вам откроется доступ к курсу «Подготовка к поиску работы».\n\nЭто практический курс, на котором вы пройдете все основные этапы подготовки к поиску работы. Уроки курса в записи, вы можете проходить их в своем темпе.\n\nПосле этого вы можете обратиться за помощью в поиске работы в центр карьеры и продолжить работать с карьерным консультантом. На последнем уроке курса будет ссылка на форму, которую необходимо заполнить для обращения в центр карьеры.',
  27: 'Карьерный план\nПостроите свою стратегию поиска работы: поставите карьерную цель, проанализируете рынок и свой опыт\nСоставите карту поиска и разработаете несколько вариантов достижения карьерной цели\nСоставите резюме, которое отобразит ваши сильные стороны\nНаучитесь отвечать на вопросы рекрутера и рассказывать о себе на собеседовании\nБудете готовы приступать к активному поиску работы\nБиблиотека рекомендаций по поиску работы\nБольшая подборка статей про поиск работы для студентов. Здесь можно найти профильные рекомендации и дополнительные материалы по подготовке и самому процессу поиска работы.\nㅤ\n\nПартнерские вакансии и стажировки\nПосле успешной подготовки к поиску вы можете откликаться на вакансии и стажировки наших партнеров в Telegram-канале.\n\nЗдесь мы публикуем предложения от работодателей, которые обратились напрямую в центр карьеры и готовы рассматривать студентов и выпускников GeekBrains. Вы получите доступ к этому каналу на курсе «Подготовка к поиску работы».\n\nЕсли появляется конкретная позиция, на которую вы откликаетесь через нас, — мы можем дать дополнительные рекомендации по резюме под конкретный запрос, чтобы шансы на положительное рассмотрение увеличились.',
  28: 'Да. Налоговый вычет — это возврат части налога на доход физических лиц. Получить его можно, например, если вы оплатили обучение.\nПодробнее о налоговом вычете на официальном сайте ФНС.\n\nЧто понадобится для налогового вычета\nОформить налоговый вычет можно по окончании календарного года, в котором оплатили обучение, но не позже трёх лет с момента оплаты. Для этого понадобятся:\n\n- Договор с образовательным учреждением — в нашем случае оферта.\n- Лицензия образовательного учреждения.\n- Платёжные документы, подтверждающие фактические расходы на обучение. Подойдут спецификация к кредитному договору или чек — они должны быть у вас на электронной почте, а также выписка по счёту — её можно запросить в поддержке банка.',
  29: 'Если вам отказали в получении налогового вычета по предоставленным документам, на сайте центрального аппарата ФНС подайте запрос «Признаётся ли мой договор (оферта) договором об образовании?». Обязательно приложите к нему оферту и отказ налоговой.\n\nПосле того как ЦА ФНС подтвердит, что оферта является договором об образовании, снова обратитесь в районную налоговую инспекцию. К письму приложите ответ центрального аппарата — он является основанием для оспаривания отказа.\n\nНапишите нам на claim@geekbrains.ru, если оферту не признают договором'}
    
def load_model():
    device = torch.device("cpu")
    model = bert_classifier.BertClassifier(model_path='cointegrated/rubert-tiny2',
            tokenizer_path='cointegrated/rubert-tiny2',
            n_classes=30,
            epochs=3,
            model_save_path=MODEL_PATH
    )
    model.model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    return model
    
def predict(model, text):
    answer = answer_class[model.predict(text)]
    return answer

def lissener():
    while True:
        if os.path.exists('question.txt'):
            break
        time.sleep(0.01)
    with open('question.txt', 'r') as f:
        question = f.read()
    os.remove('question.txt')
    print("Question: ", question)
    answer = predict(model, question)
    with open('answer.txt', 'w') as f:
        f.write(answer)
    print("Answer: ", answer)
    lissener()

if __name__ == '__main__':
    model = load_model()
    lissener()