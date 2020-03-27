# Parrot - commandline utility for movie recomendation using rutracker api
## Usage
```bash
$ ./parrot.py -h
usage: parrot.py [-h] [-s SEARCH [SEARCH ...]] [-w] [-d] [-S] [-n OPTION] [-a]

optional arguments:
  -h, --help            show this help message and exit
  -s SEARCH [SEARCH ...], --search SEARCH [SEARCH ...]
                        Query to search in topic database
  -w, --what2watch      Select n-th percentile by rating and choose random
                        entry
  -d, --repopulate      Force repopulation of the topic database
  -S, --silent          Do not output log
  -n OPTION, --option OPTION
                        Get link for n-th search result
  -a, --add             Add torrent to torrent client
$ ./parrot.py -s "lion" # prints database search results
Лев Пустыни / Lion of the Desert (Мустафа Аккад) [1981, США, Ливия, Великобритания, исторический, DVDRip] | [ 2251 * ]
$ ./parrot.py -s "lion" -n 0 # searches database and prints magnet link of the first result
magnet:?xt=urn:btih:2db52fc9607517d5c4af7c2cdd4aa925931a85a1&dn=%D0%9B%D0%B5%D0%B2%20%D0%9F%D1%83%D1%81%D1%82%D1%8B%D0%BD%D0%B8%20/%20Lion%20of%20the%20Desert%20%28%D0%9C%D1%83%D1%81%D1%82%D0%B0%D1%84%D0%B0%20%D0%90%D0%BA%D0%BA%D0%B0%D0%B4%29%20%5B1981%2C%20%D0%A1%D0%A8%D0%90%2C%20%D0%9B%D0%B8%D0%B2%D0%B8%D1%8F%2C%20%D0%92%D0%B5%D0%BB%D0%B8%D0%BA%D0%BE%D0%B1%D1%80%D0%B8%D1%82%D0%B0%D0%BD%D0%B8%D1%8F%2C%20%D0%B8%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B9%2C%20DVDRip%5D&tr=http://bt.t-ru.org/ann&tr=http://bt2.t-ru.org/ann&tr=http://bt3.t-ru.org/ann&tr=http://bt4.t-ru.org/ann&tr=http://bt5.t-ru.org/ann&tr=http://retracker.local/announce.php&tr=https://tracker.parrotlinux.org:443/announce&tr=https://tracker.opentracker.se:443/announce
$ ./parrot.py -w # gets 10 entries that are better than 70 percent of entries
0.  Рокки V / Rocky V (Сильвестр Сталлоне / Sylvester Stallone) [1990, США, драма, спорт, HDRip] | [ 83653 * ]
1.  Войны 2072 года / Новые гладиаторы / I guerrieri dell'anno 2072 / The new gladiators / Fighting centurions / Rome 2072 A.D. / W (Лючио Фульчи / Luciao Fulci) [1984, Италия, Фантастика, постапокалипсис, боевик, DVDRip] VO | [ 83486 * ]
2.  Две женщины / La ciociara (Дино Ризи / Dino Risi) [1988, Италия, Драма, DVDRip] | [ 83463 * ]
3.  Реаниматор / Re-Animator (Стюарт Гордон / Stuart Gordon) [1985, США, ужасы, фантастика, DVDRip] AVO (Карцев) | [ 83447 * ]
4.  Суббота, воскресенье и пятница / Sabato, domenica e venerdi' (Франко Кастеллано / Franco Castellano, Паскуале Феста Кампаниле / Pasquale Festa Campanile, Серджо Мартино / Sergio Martino) [1979, Италия, Испания, Комедия, DVDRip] | [ 83430 * ]
5.  Презумпция невиновности / Presumed Innocent (Алан Дж. Пакула / Alan J. Pakula) [1990, США, Триллер, Детектив, Драма, Криминал, HDRip] Dub | [ 83417 * ]
6.  Та еще парочка (DVDRip) / Two of a Kind (Джон Херцфелд) [1983, США, фэнтези, комедия, мелодрама, DVDRip] | [ 82911 * ]
7.  Месть придурков / Revenge of the Nerds (Джэфф Кэнью /Jeff Kanew) [1984, США, Комедия, Триллер, DVDRip] | [ 82887 * ]
8.  Почти ангел / Almost an angel (Джон Корнэлл / John Cornell) [1990, США, комедия, DVDRip] | [ 82825 * ]
9.  Звездный Путь II. Гнев Хана/Star Trek II The Wrath of Khan(1982 DVDRip) | [ 82620 * ]
$ ./parrot.py -wn 0 # select the first entry and print the magnet link 
magnet:?xt=urn:btih:0fc8bc951836411f7ac422aa5bf2c3a8875adef6&dn=%D0%A0%D0%BE%D0%BA%D0%BA%D0%B8%20V%20/%20Rocky%20V%20%28%D0%A1%D0%B8%D0%BB%D1%8C%D0%B2%D0%B5%D1%81%D1%82%D1%80%20%D0%A1%D1%82%D0%B0%D0%BB%D0%BB%D0%BE%D0%BD%D0%B5%20/%20Sylvester%20Stallone%29%20%5B1990%2C%20%D0%A1%D0%A8%D0%90%2C%20%D0%B4%D1%80%D0%B0%D0%BC%D0%B0%2C%20%D1%81%D0%BF%D0%BE%D1%80%D1%82%2C%20HDRip%5D&tr=http://bt.t-ru.org/ann&tr=http://bt2.t-ru.org/ann&tr=http://bt3.t-ru.org/ann&tr=http://bt4.t-ru.org/ann&tr=http://bt5.t-ru.org/ann&tr=http://retracker.local/announce
$ ./parrot -wan 0 # runs 'add torrent command' with the magnet link as argument
```
## TODO
1. ~Add "what to watch" feature~
2. ~Add watched movies table in DB~
3. Add "to watch list" that will ignore rating limit
4. ~Add configurable transmission remote command for adding torrents~
5. ~Parallellize rating calculation.~(Beta)
