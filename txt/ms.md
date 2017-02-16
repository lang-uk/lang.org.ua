# Мікросервіси lang-uk

[Мікросервіси lang-uk](https://github.com/chaliy/lang-uk-ms) — це можливість легко запустити і використовувати основні інструменти, які розроблені нашою командою. Технічно це реалізується з використанням технологій Swagger і Docker.

На даний момент в наявності є наступні сервіси:

- Токенізація
- Український, російський та англійський NER
- Лематизація з використанням можливостей бібліотеки [nlp_uk](https://github.com/brown-uk/nlp_uk)
- Розпізнавання мови з використанням можливостей бібліотеки [WILD](https://github.com/vseloved/wiki-lang-detect)

Проект `lang-uk-ms` дозволяє запустити всі мікросервіси одночасно і отримати доступ до них через веб-інтерфейс.

Приклад HTTP-запиту:

```
$ curl -X POST -H "Content-Type: application/json" -d "{'text': 'Несе Галя'}" http://localhost:8080/lang-detect/wiki/detect
[["uk",0.83333343],["bg",0.16666652]]
```

Розробка Docker-скриптів виконана [Михайлом Чалієм](http://chaliy.name/).


## Мікросервіс NER

[Мікросервіс NER](https://github.com/chaliy/ner-ms) дозволяє здійснити NER-розмітку токенізованого тексту з використанням [моделей](http://lang.org.ua/models/), натренованих з допомогою бібліотеки MITIE для української, російської та англійської мов (в залежності від вибору відповідного Dockerfile при запуску сервісу).

Приклад HTTP-запиту:

```
curl -X POST -H "Content-Type: application/json" -d '{ "tokens": ["Несе","Галя","воду",",","Коромисло","гнеться" ]}' http://localhost:8080/
```

## Мікросервіс NLP_UK

[Мікросервіс на основі бібліотеки NLP_UK](https://github.com/arysin/api_nlp_uk) дає змогу виконати лематизацію вхідного тексту за словником [dict_uk](https://github.com/brown-uk/dict_uk), яка також включає його токенізацію.

```
curl -X POST -H "Content-Type: application/json" -d "{'text': 'Сьогодні у продажі. 12-те зібрання творів 1969 р. І. П. Котляревського.'}" http://localhost:8080/lemmatize/
```


## Мікросервіс розпізнавання мови (WILD)

[Мікросервіс WILD](https://github.com/vseloved/wiki-lang-detect) дозволяє розпізнати мову вхідного тексту з переліку 156 мов, які використовуються в інтернеті, за допомогою бібліотеки `wiki-lang-detect`.

Приклад HTTP-запиту:

```
curl -X POST -H "Content-Type: application/json" -d "{'text': 'Несе Галя'}" http://localhost:8080/
```

