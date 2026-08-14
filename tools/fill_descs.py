# -*- coding: utf-8 -*-
"""Fill the 36 empty culture/trait desc lines in th_country_l_*.yml (5 languages)."""
import re
from pathlib import Path

root = Path(r'F:\Paradox Interactive\Europa Universalis V\mod\Touhou Universalis II')

D = {
 'acgv_touhou_fairy_culture_desc': {
  'en': "Lighthearted spirits of nature born from the land's vitality, flitting about Gensokyo in carefree mischief. Frail but numerous, their pranks shape the everyday wonder of the realm.",
  'zh': "由大地生机所生的自然精灵，在幻想乡中无忧无虑地嬉闹。身躯纤弱却为数众多，她们的恶作剧造就了这片土地日常的奇迹。",
  'ja': "大地の活力から生まれた自然の精霊。幻想郷を無邪気に飛び回り、いたずらを繰り返す。儚いが数多く、その悪戯は郷の日常の不思議を形作る。",
  'ko': "대지의 활기에서 태어난 자연의 정령. 환상향을 천진난만하게 날아다니며 장난을 친다. 나약하지만 수가 많고, 그 장난이 이 땅의 일상적 신비를 만든다.",
  'ru': "Беззаботные духи природы, рождённые из жизненной силы земли, порхающие по Генсокё в беспечных шалостях. Хрупкие, но многочисленные, их проказы творят повседневное чудо этих земель.",
 },
 'acgv_touhou_doubutsu_goast_culture_desc': {
  'en': "Beasts who have awakened as youkai, from wise foxes and great tanuki to humble cats and rabbits. They walk the path of beasts, gaining power through age and legend.",
  'zh': "觉醒为妖怪的兽类，从睿智的狐与豪迈的狸，到平凡的猫与兔。它们行于兽之道，借岁月与传说积累力量。",
  'ja': "妖怪として目覚めた獣たち。賢き狐、豪放な狸から、気取らぬ猫や兎に至るまで。獣の道を歩み、歳月と伝説によって力を増す。",
  'ko': "요괴로 깨어난 짐승들. 지혜로운 여우와 호탕한 너구리에서 소박한 고양이와 토끼에 이르기까지. 짐승의 길을 걸으며 세월과 전설로 힘을 얻는다.",
  'ru': "Звери, пробудившиеся как ёкаи — от мудрых лисиц и великих тануки до скромных кошек и кроликов. Они идут звериным путём, обретая силу через возраст и легенды.",
 },
 'acgv_touhou_haniyasushin_culture_desc': {
  'en': "The divine artisan of the earth, shaping clay and stone into vessels of life. Guardians of craft and creation, they dwell where soil meets spirit.",
  'zh': "大地之神工，以粘土与岩石塑成生命的容器。作为技艺与创造的守护者，他们栖于泥土与灵性交汇之处。",
  'ja': "大地の神工。粘土と岩石を以て命の器を形作る。技芸と創造の守護者にして、土と霊の交わる地に住まう。",
  'ko': "대지의 신공. 진흙과 돌로 생명의 그릇을 빚는다. 공예와 창조의 수호자로서 흙과 영혼이 만나는 곳에 거한다.",
  'ru': "Божественный мастер земли, творящий из глины и камня сосуды жизни. Стражи ремесла и созидания, они обитают там, где почва встречается с духом.",
 },
 'acgv_touhou_goast_culture_desc': {
  'en': "Wandering souls bound to Gensokyo by lingering regrets. Ethereal and melancholic, they drift between the living world and the afterlife.",
  'zh': "因未尽之执念而滞留于幻想乡的漂泊之魂。虚幻而哀伤，他们在生者之世与彼岸之间徘徊。",
  'ja': "未練の想いに縛られ幻想郷に留まる漂う魂。幽幻にして哀愁を帯び、生者の世と彼岸の間を漂う。",
  'ko': "남은 미련에 묶여 환상향에 머무는 떠도는 영혼. 유령처럼 애처롭고, 산 자의 세계와 저승 사이를 떠돈다.",
  'ru': "Блуждающие души, привязанные к Генсокё неотпущенными сожалениями. Бесплотные и печальные, они дрейфуют меж миром живых и загробным миром.",
 },
 'acgv_touhou_eastern_kami_culture_desc': {
  'en': "The gods of Gensokyo's mountains, shrines, and sacred sites. Ancient and aloof, they are sustained by faith and the reverence of the land's people.",
  'zh': "幻想乡山岳、神社与圣地的神明。古老而超然，他们依靠信仰与土地上子民的敬仰而存续。",
  'ja': "幻想郷の山、神社、霊地に座す神々。古くして高みにあり、信仰と土地の人々の尊崇によって支えられる。",
  'ko': "환상향의 산, 신사, 성지에 자리한 신들. 오래되고 초연하며, 신앙과 땅의 백성들의 존경으로 유지된다.",
  'ru': "Боги гор, святилищ и священных мест Генсокё. Древние и отстранённые, они живут верой и почитанием людей этой земли.",
 },
 'acgv_touhou_oni_culture_desc': {
  'en': "Mighty and proud denizens of the mountains, masters of brute strength and earthly desires. Once feared throughout Gensokyo, they now dwell largely in seclusion.",
  'zh': "强大而骄傲的山之居民，蛮力与尘世欲望的主人。曾令整个幻想乡畏惧，如今大多隐居于世。",
  'ja': "強壮にして誇り高き山の住人。剛力と世俗の欲望の主。かつて幻想郷全域に恐れられたが、今は多くが隠遁の身。",
  'ko': "강대하고 자존심 강한 산의 거주자. 괴력과 세속적 욕망의 지배자. 한때 환상향 전체가 두려워했으나, 지금은 대부분 은거한다.",
  'ru': "Могучие и гордые обитатели гор, владыки грубой силы и земных желаний. Некогда внушавшие страх всему Генсокё, ныне они живут по большей части в уединении.",
 },
 'acgv_touhou_reonna_culture_desc': {
  'en': "Bestial youkai in whom raw instinct and wild power reign. Honest and straightforward, they value strength above all and disdain trickery.",
  'zh': "凭本能与野性之力而活的妖兽。坦率直爽，视力量为至上，鄙夷诡计。",
  'ja': "野性の本能と荒々しい力が支配する獣の妖怪。率直で実直、何より力を尊び、小賢しさを嫌う。",
  'ko': "본능과 야성의 힘이 지배하는 짐승 요괴. 솔직하고 직선적이며 무엇보다 힘을 숭상하고 책략을 싫어한다.",
  'ru': "Звериные ёкаи, в которых царят первобытный инстинкт и дикая сила. Честные и прямые, они превыше всего ценят силу и презирают хитрость.",
 },
 'acgv_touhou_eastern_youkai_culture_desc': {
  'en': "The myriad monsters and spirits of Gensokyo, born of human fear and wonder. Each is unique, bound by its own nature, legend, and weakness.",
  'zh': "由人类的恐惧与惊奇所生的幻想乡万般妖怪。各自独一无二，受自身的本性、传说与弱点所束缚。",
  'ja': "人間の恐怖と驚異から生まれた幻想郷の数多の妖怪。一匹一匹が唯一無二、自らの性質・伝説・弱点に縛られる。",
  'ko': "인간의 공포와 경이에서 태어난 환상향의 무수한 요괴. 하나하나가 독특하며, 각자의 본성과 전설, 약점에 묶여 있다.",
  'ru': "Бесчисленные монстры и духи Генсокё, рождённые людским страхом и изумлением. Каждый уникален, скован собственной природой, легендой и слабостью.",
 },
 'acgv_touhou_lunar_culture_desc': {
  'en': "The eternal people of the Moon, heirs of a civilization of unmatched purity and longevity. They look upon the earthbound with distant, untroubled eyes.",
  'zh': "永生的月之民，继承了无与伦比的纯净与长寿文明。他们以遥远而安详的目光俯视大地众生。",
  'ja': "月の永遠の民。比類なき純粋さと長寿の文明の継承者。地上の者を遠い、穏やかな目で見下ろす。",
  'ko': "달의 영원한 백성. 비할 데 없는 순수함과 장수의 문명의 후계자. 땅에 사는 자들을 멀고 평온한 눈으로 내려다본다.",
  'ru': "Вечный народ Луны, наследники цивилизации несравненной чистоты и долголетия. На земных они взирают отстранённым, безмятежным взором.",
 },
 'acgv_touhou_scarlet_culture_desc': {
  'en': "Vampires and their servants dwelling within the Scarlet Devil Mansion. A house of crimson nights, elegant decadence, and thirst for the forbidden.",
  'zh': "栖身于红魔馆的吸血鬼及其仆从。猩红之夜、优雅的颓废与对禁忌之物的渴求之家。",
  'ja': "紅魔館に住まう吸血鬼とその従者たち。紅き夜、優雅なる退廃、そして禁忌への渇望の館。",
  'ko': "홍마관에 거하는 뱀파이어와 그 시종들. 새빨간 밤, 우아한 퇴폐, 그리고 금지된 것에 대한 갈망의 저택.",
  'ru': "Вампиры и их слуги, обитающие в Особняке Алой Дьяволицы. Дом багровых ночей, изящного декаданса и жажды запретного.",
 },
 'acgv_touhou_tsugumogami_culture_desc': {
  'en': "Tools and treasures that have gained life after a century of existence. They serve their masters faithfully — or rebel, should they be discarded.",
  'zh': "度过百年岁月后获得生命的器物与珍宝。它们忠心事主——若被抛弃，则起而反抗。",
  'ja': "百年の時を経て命を得た道具と宝物。主に忠実に仕えるが、捨てられれば反逆する。",
  'ko': "백 년의 세월을 넘어 생명을 얻은 도구와 보물. 주인에게 충실히 섬기지만, 버려지면 반역한다.",
  'ru': "Инструменты и сокровища, обретшие жизнь после столетия существования. Они верно служат хозяевам — или восстают, если их бросили.",
 },
 'acgv_touhou_makai_culture_desc': {
  'en': "The demonic realm beyond the boundary, ruled by the Magician of Makai. A land of magic, lawlessness, and schemes both grand and petty.",
  'zh': "境界彼端的魔界，由魔界的魔法使统治。魔法与无序之地，宏伟与琐碎的阴谋交织其间。",
  'ja': "境界の彼方に広がる魔の世界、魔界の魔法使いが治める地。魔法と無法の国、壮大にして些細な企みが渦巻く。",
  'ko': "경계 너머의 마계, 마계의 마법사가 다스리는 땅. 마법과 무법의 나라, 웅대하고도 사소한 음모가 소용돌이친다.",
  'ru': "Демоническое царство за пределами границы, правящееся Магом Макай. Земля магии, беззакония и замыслов — великих и мелких.",
 },
 'acgv_touhou_poltergeist_culture_desc': {
  'en': "Phantom musicians who haunt the Scarlet Devil Mansion with their spectral performances. Mischievous and gifted, they make melody of the unseen.",
  'zh': "以幻影演奏萦绕红魔馆的骚灵乐手。顽皮而才华横溢，她们以无形之音编织旋律。",
  'ja': "紅魔館に幻の演奏を響かせる騒霊の音楽家たち。いたずら好きで才に溢れ、見えぬものから旋律を紡ぐ。",
  'ko': "홍마관에 환영의 연주를 울리는 폴터가이스트 음악가들. 장난기 많고 재능이 넘치며, 보이지 않는 것에서 선율을 짠다.",
  'ru': "Призрачные музыканты, наполняющие Особняк Алой Дьяволицы своими эфемерными выступлениями. Озорные и одарённые, они творят мелодию из незримого.",
 },
 'acgv_touhou_seikai_culture_desc': {
  'en': "The serene paradise of immortals, where the enlightened practice arts of transcendence. Time flows gently, and sages refine their immortality.",
  'zh': "仙人的宁静乐园，开悟者在其中修习超脱之术。时光缓缓流淌，仙人们精进着他们的永生。",
  'ja': "仙人の静かな楽園。悟りし者たちが超脱の技を修め、時は穏やかに流れ、仙たちは不老を磨く。",
  'ko': "선인의 고요한 낙원. 깨달은 자들이 초탈의 예를 닦고, 시간은 부드럽게 흐르며, 선인들은 불로를 다듬는다.",
  'ru': "Безмятежный рай бессмертных, где просветлённые постигают искусства трансценденции. Время течёт мягко, и мудрецы оттачивают своё бессмертие.",
 },
 'acgv_touhou_shinkirou_culture_desc': {
  'en': "The people of the mirage, dwelling at the edge of reality and illusion. Masters of the dreamlike, they blur the line between what is and what seems.",
  'zh': "蜃气楼之民，栖于现实与幻象的边缘。身为梦幻的主宰，他们模糊了存在与表象的界限。",
  'ja': "蜃気楼の民。現実と幻の境に住まい、夢幻を操る者たち。あるものと見えるものの境界を曖昧にする。",
  'ko': "신기루의 백성. 현실과 환영의 경계에 거하며, 몽환을 다루는 자들. 있는 것과 보이는 것의 경계를 흐리게 한다.",
  'ru': "Народ миража, обитающий на грани реальности и иллюзии. Владыки грёз, они размывают черту между тем, что есть, и тем, что кажется.",
 },
 'acgv_touhou_western_youkai_culture_desc': {
  'en': "Foreign monsters from the West who have crossed the boundary into Gensokyo. Ancient and worldly, they bring the legends of distant lands.",
  'zh': "越过境界进入幻想乡的西方异邦之魔。古老而世故，他们带来了远方的传说。",
  'ja': "境界を越えて幻想郷に来た西方の異国の魔物。古くして世慣れ、遠き地の伝説を携える。",
  'ko': "경계를 넘어 환상향에 온 서방의 이국 괴물들. 오래되고 세상 물정에 밝으며, 머나먼 땅의 전설을 가져온다.",
  'ru': "Чужеземные монстры Запада, пересекшие границу в Генсокё. Древние и искушённые, они приносят легенды дальних земель.",
 },
 'acgv_touhou_kaguya_culture_desc': {
  'en': "The court of the Moon Princess at Eientei, guarded by the Eternal Lunarian. Here, medicine and alchemy serve eternity itself.",
  'zh': "永远亭中月之公主的宫廷，由永生的月人守护。在这里，医药与炼金术为永恒本身效力。",
  'ja': "永遠亭に在る月の姫の宮廷、永遠の月人が守る。ここでは医術と錬金術が永遠そのものに仕える。",
  'ko': "영원정의 달의 공주 궁정, 영원한 달인이 지킨다. 이곳에서 의술과 연금술은 영원 그 자체를 섬긴다.",
  'ru': "Двор Лунной Принцессы в Эйэнтэй, охраняемый Вечной Лунянкой. Здесь медицина и алхимия служат самой вечности.",
 },
 'acgv_touhou_myoukai_culture_desc': {
  'en': "The vast netherworld where the dead linger in quiet gardens. Its spectral residents tend to their duties in serene stillness.",
  'zh': "死者静驻于庭园之中的广大冥界。其幽灵居民在安详的寂静中履行着各自的职责。",
  'ja': "死者が静かな庭に留まる広大な冥界。その幽霊たちは穏やかな静寂の中で務めを果たす。",
  'ko': "죽은 자가 고요한 정원에 머무는 광대한 명계. 그 유령 주민들은 평온한 침묵 속에서 임무를 수행한다.",
  'ru': "Бескрайний загробный мир, где мёртвые пребывают в тихих садах. Его призрачные обитатели несут свой долг в безмятежной тишине.",
 },
 'acgv_touhou_kappa_culture_desc': {
  'en': "River-dwelling youkai who excel in engineering and invention. Curious, industrious, and ever fond of cucumbers, they guard Gensokyo's waterways.",
  'zh': "擅长机关与发明的河之妖怪。好奇、勤勉、永远偏爱黄瓜，他们守护着幻想乡的水道。",
  'ja': "河に住み、工学と発明に長けた妖怪。好奇心旺盛で勤勉、常に胡瓜を愛し、幻想郷の水路を守る。",
  'ko': "강에 사는, 공학과 발명에 능한 요괴. 호기심 많고 부지런하며 언제나 오이를 좋아하고, 환상향의 수로를 지킨다.",
  'ru': "Речные ёкаи, искусные в инженерии и изобретательстве. Любопытные, трудолюбивые и вечно неравнодушные к огурцам, они хранят водные пути Генсокё.",
 },
 'acgv_touhou_yamawaru_culture_desc': {
  'en': "Childlike spirits of the mountains, kin to the kappa. They dwell on the peaks, playing pranks on travelers and aiding those they take a liking to.",
  'zh': "山中的孩童般精灵，河童的近亲。他们居于峰顶，捉弄旅人，也会帮助自己中意的人。",
  'ja': "山に住まう童のような精霊、河童の近親。峰に暮らし、旅人に悪戯をし、気に入った者には手を貸す。",
  'ko': "산에 사는 아이 같은 정령, 갓파의 친척. 봉우리에 살며 여행자를 골탕 먹이고, 마음에 드는 자를 돕는다.",
  'ru': "Детоподобные духи гор, родичи капп. Они обитают на вершинах, проказничают над путниками и помогают тем, кто им приглянулся.",
 },
 'acgv_touhou_tengu_culture_desc': {
  'en': "The proud mountain youkai who command the winds and the heights. Swift and disciplined, they watch over Gensokyo from above, keepers of news and tradition.",
  'zh': "统御风与高天的骄傲山妖。迅捷而严明，他们自高处俯瞰幻想乡，是消息与传统的守护者。",
  'ja': "風と高みを統べる誇り高き山の妖怪。俊敏にして規律正しく、幻想郷を高みから見守り、風聞と伝統を守る。",
  'ko': "바람과 높은 곳을 다스리는 자존심 강한 산 요괴. 민첩하고 규율이 엄격하며, 높은 곳에서 환상향을 지켜보고 소문과 전통을 지킨다.",
  'ru': "Гордые горные ёкаи, повелевающие ветрами и высотами. Стремительные и дисциплинированные, они наблюдают за Генсокё свыше, хранители вестей и традиций.",
 },
 'acgv_touhou_western_kami_culture_desc': {
  'en': "Gods who have crossed into Gensokyo from the Outside World, seeking faith and a new home. They blend foreign reverence with the land's native beliefs.",
  'zh': "为寻求信仰与新家而从外界越过境界的神明。他们将外来的崇敬与这片土地的本土信仰相融合。",
  'ja': "外界から境界を越え、信仰と新たな居を求めて幻想郷に来た神々。外来の崇拝と土地の信仰を織り交ぜる。",
  'ko': "신앙과 새 보금자리를 찾아 외부 세계에서 경계를 넘어온 신들. 외래의 숭배와 이 땅의 토착 신앙을 섞는다.",
  'ru': "Боги, пересёкшие границу из Внешнего Мира в поисках веры и нового дома. Они сплетают чужеземное почитание с исконными верованиями этой земли.",
 },
 'acgv_touhou_higan_culture_desc': {
  'en': "The far shore of the Sanzu River, where the dead are judged. Its residents — shinigami and ferrymen — carry out the impartial work of the afterlife.",
  'zh': "三途川的彼岸，亡者在此受审。其居民——死神与摆渡人——执行着冥界不偏不倚的公务。",
  'ja': "三途の川の彼方、死者が裁かれる岸。その住人たる死神や渡し守は、冥土の公平な務めを果たす。",
  'ko': "삼도천의 저편, 죽은 자가 심판받는 언덕. 그 주민인 사신과 나룻배 사공은 저승의 공정한 임무를 수행한다.",
  'ru': "Дальний берег реки Сандзу, где судят мёртвых. Его обитатели — синигами и лодочники — несут беспристрастную службу загробного мира.",
 },
 'acgv_touhou_hibito_culture_desc': {
  'en': "Tiny folk of hidden realms, whose crafts and remedies are of extraordinary quality. They live in the interstices of the world, rarely seen and greatly prized.",
  'zh': "隐秘国度的小人一族，其工艺与药方品质非凡。他们居于世界的缝隙之中，难得一见，备受珍视。",
  'ja': "隠れ里の小さき民。その工芸と薬は格別の品質を誇る。世界の狭間に暮らし、滅多に姿を見せず、重宝される。",
  'ko': "숨겨진 세계의 작은 백성. 그 공예와 약은 비범한 품질을 자랑한다. 세계의 틈새에 살며 좀처럼 모습을 드러내지 않고 크게 귀중히 여겨진다.",
  'ru': "Крошечный народ скрытых миров, чьи ремёсла и снадобья отличаются необычайным качеством. Они живут в промежутках мира — редко видимые и высоко ценимые.",
 },
 'acgv_touhou_kamui_culture_desc': {
  'en': "Great spirits of the northern lands who hold dominion over mountains and forests. Worshipped and feared in equal measure, they are forces of nature incarnate.",
  'zh': "统御山岳与森林的北方大国灵。既受崇拜亦令人畏惧，他们是自然之力的化身。",
  'ja': "北の地の大いなる霊。山と森を支配する。崇められると同時に恐れられ、自然の力の化身なり。",
  'ko': "북방의 위대한 영령. 산과 숲을 지배한다. 숭배와 두려움을 동시에 받으며, 자연의 힘 그 자체의 화신이다.",
  'ru': "Великие духи северных земель, властвующие над горами и лесами. Почитаемые и страшимые в равной мере, они — воплощение сил природы.",
 },
 'acgv_touhou_yakubyougami_culture_desc': {
  'en': "The plague god, who brings misfortune and disease wherever she walks. Feared and shunned, yet capable of lifting the very curses she bestows.",
  'zh': "行至何处便带去灾厄与疾病的疫病神。令人畏惧、遭人回避，却也能解除自己所降下的诅咒。",
  'ja': "歩む先々に災厄と病を運ぶ疫病神。恐れられ疎まれつつも、自ら授けた呪いを解く力を持つ。",
  'ko': "걸음마다 재앙과 병을 옮기는 역병신. 두려움과 배척을 받지만, 자신이 내린 저주를 거둘 힘도 지녔다.",
  'ru': "Бог чумы, несущий несчастья и болезни, куда бы ни ступил. Его страшатся и избегают, но он способен снимать те самые проклятия, что насылает.",
 },
 'acgv_touhou_chireiden_culture_desc': {
  'en': "The underground palace of the Old Hell, where the Palace of the Earth Spirits holds court. Its denizens govern the geothermal depths and their fiery beasts.",
  'zh': "旧地狱的地灵殿，地灵们在此执掌宫廷。其居民统御着地热深渊与其间的火之野兽。",
  'ja': "旧地獄の地下宮殿、地霊殿。地霊たちが政を執る。その住人は地熱の深みと炎の獣たちを統べる。",
  'ko': "구 지옥의 지하 궁전, 지령전. 지령들이 정사를 펼친다. 그 주민들은 지열의 심연과 불꽃의 짐승들을 다스린다.",
  'ru': "Подземный дворец Старого Ада, где правит Дворец Земных Духов. Его обитатели властвуют над геотермальными глубинами и огненными зверями.",
 },
 'acgv_touhou_ningyou_culture_desc': {
  'en': "The living dolls of the supernatural world, from the seven that slumber in the cellar to the countless puppets of magical performers. Small vessels, great hearts.",
  'zh': "超自然世界的人偶，从地下室沉眠的七人偶到魔法使们数之不尽的傀儡。小小的躯壳，承载着伟大的心灵。",
  'ja': "超常の世界の人形たち。地下室に眠る七人形から、魔法使いの無数の操り人形まで。小さき器に、大きな心。",
  'ko': "초자연 세계의 살아있는 인형들. 지하실에 잠든 일곱 인형에서 마법사의 무수한 꼭두각시까지. 작은 그릇에 큰 마음.",
  'ru': "Живые куклы сверхъестественного мира — от семи спящих в подвале до бесчисленных марионеток магических исполнителей. Малые сосуды, великие сердца.",
 },
 'acgv_touhou_yumemi_culture_desc': {
  'en': "The shifting realm of dreams and fantasy, where imagination takes form. Its residents drift through the sleeping minds of the world.",
  'zh': "梦境与幻想的流变之国，想象在此化作实体。其居民漂游于世间沉睡的心灵之中。",
  'ja': "夢と幻想の流転する国、想像が形を取る地。その住人は世界の眠る心の中を漂う。",
  'ko': "꿈과 환상이 유전하는 나라, 상상이 형태를 취하는 곳. 그 주민들은 세상의 잠든 마음 속을 떠돈다.",
  'ru': "Зыбкое царство грёз и фантазий, где воображение обретает форму. Его обитатели дрейфуют сквозь спящие умы мира.",
 },
 'acgv_touhou_yakumo_culture_desc': {
  'en': "The maze-like homestead at the edge of Gensokyo, home of the boundary manipulator. A place where directions are lost and time grows strange.",
  'zh': "幻想乡边缘的迷宫般的居所，境界操纵者的家园。一个方向会迷失、时间会变得奇异的所在。",
  'ja': "幻想郷の端に在る迷路のような屋敷、境界を操る者の住まい。方角は失われ、時が奇妙になる場所。",
  'ko': "환상향 가장자리의 미로 같은 집, 경계를 다루는 자의 거처. 방향이 사라지고 시간이 이상해지는 곳.",
  'ru': "Похожее на лабиринт поместье на краю Генсокё, дом манипулятора границами. Место, где теряются направления и странным становится время.",
 },
 'acgv_touhou_gensokyo_hito_culture_desc': {
  'en': "The ordinary people of the Human Village, who live alongside youkai under the Great Barrier. Fragile in body, they are resilient in spirit, and their craft sustains the land.",
  'zh': "人间之里的凡人，在大结界下与妖怪比邻而居。身体纤弱，精神坚韧，他们的技艺支撑着这片土地。",
  'ja': "人間の里の普通人。大結界の下、妖怪と隣り合って生きる。身は脆くとも心は強く、その技が郷を支える。",
  'ko': "인간 마을의 평범한 사람들. 대결계 아래에서 요괴와 이웃하며 산다. 몸은 나약하지만 마음은 강하고, 그 솜씨가 이 땅을 지탱한다.",
  'ru': "Обычные люди Человеческой Деревни, живущие бок о бок с ёкаями под Великим Барьером. Хрупкие телом, они стойки духом, и их ремесло держит эту землю.",
 },
 'acgv_touhou_myouren_culture_desc': {
  'en': "The Buddhist temple whose monks and believers shelter youkai seeking redemption. Here, faith offers a second path for even the most wayward spirits.",
  'zh': "接纳寻求救赎之妖怪的佛寺，僧侣与信徒在此庇护他们。在这里，信仰为最迷途的魂魄也准备了第二条路。",
  'ja': "救済を求める妖怪を僧侶と信徒が慈しみ受け入れる仏寺。ここでは信仰が最も迷える霊にも第二の道を与える。",
  'ko': "구원을 구하는 요괴를 스님과 신자들이 품어 주는 불교 사찰. 이곳에서 신앙은 가장 방황하는 영혼에게도 두 번째 길을 준다.",
  'ru': "Буддийский храм, чьи монахи и верующие дают приют ёкаям, ищущим искупления. Здесь вера открывает второй путь даже самым заблудшим духам.",
 },
 'acgv_touhou_tennin_culture_desc': {
  'en': "The celestial realm above Gensokyo, where tennin and divine attendants dwell in eternal bliss. Their music and dances echo through the clouds.",
  'zh': "幻想乡之上的天界，天人与其神侍在永恒的极乐中安居。他们的乐声与舞姿回荡于云间。",
  'ja': "幻想郷の上の天界。天人と神の従者たちが永遠の楽に住まう。その楽と舞は雲間に響く。",
  'ko': "환상향 위의 천계. 천인과 신의 시종들이 영원한 즐거움 속에 거한다. 그 음악과 춤은 구름 사이에 울려 퍼진다.",
  'ru': "Небесное царство над Генсокё, где тэннин и божественные слуги пребывают в вечном блаженстве. Их музыка и танцы разносятся среди облаков.",
 },
 'acgv_touhou_tokoyo_culture_desc': {
  'en': "The eternal land beyond the sea, from which ancient treasures and immortals once came. A place of legend that exists beyond the reach of time.",
  'zh': "海之彼方的常世之国，古老的珍宝与仙人曾由此而来。一个存在于时间之外的传说之地。",
  'ja': "海の彼方の常世の国。いにしえの宝と仙人はここより来たる。時の及ばぬ所に在る伝説の地。",
  'ko': "바다 건너의 상세(常世)의 나라. 고대의 보물과 선인이 이곳에서 왔다. 시간이 닿지 않는 곳에 있는 전설의 땅.",
  'ru': "Вечная земля за морем, откуда некогда пришли древние сокровища и бессмертные. Легендарное место, лежащее вне досягаемости времени.",
 },
 'touhou_reimu_traits_desc': {
  'en': "The Hakurei shrine maiden, who resolves the incidents of Gensokyo with danmaku and conviction. Where she stands, the balance of the realm is kept.",
  'zh': "以弹幕与信念解决幻想乡异变的博丽巫女。她所立之处，便是这片土地的平衡所在。",
  'ja': "弾幕と信念で幻想郷の異変を解決する博麗の巫女。彼女の立つ所に、郷の均衡あり。",
  'ko': "탄막과 신념으로 환상향의 이변을 해결하는 하쿠레이 무녀. 그녀가 서 있는 곳에, 이 땅의 균형이 있다.",
  'ru': "Жрица Хакурэй, разрешающая инциденты Генсокё данмаку и убеждённостью. Где она стоит — там хранится равновесие этих земель.",
 },
 'touhou_akyuu_traits_desc': {
  'en': "The young chronicler of the Human Village, whose dream is to one day record the wonders of Gensokyo in a book that rivals the Gensokyo Chronicle.",
  'zh': "人间之里的年轻记述者，她的梦想是有朝一日写下一本堪与《幻想乡缘起》媲美、记录幻想乡奇观的书籍。",
  'ja': "人間の里の若き記録者。いつか幻想郷の不思議を『幻想郷縁起』に並ぶ書物に書き残すのが夢。",
  'ko': "인간 마을의 젊은 기록자. 언젠가 환상향의 신비를 《환상향연기》에 버금가는 책으로 남기는 것이 꿈이다.",
  'ru': "Юная летописица Человеческой Деревни, мечтающая однажды запечатлеть чудеса Генсокё в книге, что сравнится с «Хрониками Генсокё».",
 },
}

FILES = {
 'en': root / 'main_menu' / 'localization' / 'english' / 'th_country_l_english.yml',
 'zh': root / 'main_menu' / 'localization' / 'simp_chinese' / 'th_country_l_simp_chinese.yml',
 'ja': root / 'main_menu' / 'localization' / 'japanese' / 'th_country_l_japanese.yml',
 'ko': root / 'main_menu' / 'localization' / 'korean' / 'th_country_l_korean.yml',
 'ru': root / 'main_menu' / 'localization' / 'russian' / 'th_country_l_russian.yml',
}

for lang, path in FILES.items():
    lines = path.read_text(encoding='utf-8-sig').splitlines(keepends=True)
    fixed = 0
    out = []
    for line in lines:
        m = re.match(r'^(\s+)([A-Za-z0-9_]+):\s*""\s*$', line.rstrip('\r\n'))
        if m and m.group(2) in D:
            val = D[m.group(2)][lang]
            out.append(f"{m.group(1)}{m.group(2)}: \"{val}\"\n")
            fixed += 1
        else:
            out.append(line)
    if fixed:
        path.write_bytes(b'\xef\xbb\xbf' + ''.join(out).encode('utf-8'))
        print(f'{lang}: fixed {fixed}')
    else:
        print(f'{lang}: no empty descs found')
