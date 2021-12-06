import discord
from typing import List, Optional
cog_help = {
    "Fun": """
        Fun commands for everyone!!

        Fun Commands
        `.ai`
        `.akinator`
        `.annoy` – Usage: annoy @b1nzy#1337 50
        `.asktrump` – Ask Donald Trump a question!
        `.beer` – Give someone a beer! 🍻
        `.britainify` – Can you pass me a bo'le o' wo'e'r
        `.clownrate` – Reveal someone's clownery.
        `.coinflip` – Coinflip!
        `.cool`
        `.compliment` – Compliment someone!
        `.dadjoke` – Read a random dad joke
        `.dare`
        `.darkjoke` – Read a random dark joke
        `.eightball` – "The eight ball guides you in every part of you life"
        `.f` – Press F to pay respect
        `.fact` – Generates a Random Fact
        `face` - Gives a randomm face
        `.hit` – To settle a fight the violent way
        `.hotcalc` – Returns a random percent for how hot is a discord user
        `.iqrate` – 100% legit IQ test.
        `.numberfact` – Get a fact about a number.
        `.owofy` – Converts your message in UwUs. its not worth trying, trust me.
        `.rainbow` – Make a happy rainbow!
        `.randomcomic` – Get a comic from xkcd.
        `.roast`
        `.sanitycheck` – Check your sanity.
        `.simprate` – Find out how much someone is simping for something.
        `.slap` – when someone acts just wayy too dumb
        `.sus` – Sussu baka
        `.talk_rude` – insults the sender... better not do this
        `.tenor` – Random gif from tenor
        `.thank` – Thank someone!
        `.thankcount`
        `.truth`
        `.webhook` - Creates a temperory webhook to mimic yourself!""",

    "Config":"""
        Make Spacebot your own !!!

        censoredwords         Get the list of censored words of the server
        changeprefix          Change the prefix of the bot
        copyemoji             Copy an emoji from another server to your own
        fotd                  Enables the fact of the day to be sent to the respect...
        memechannel           Automatically adds reactions to memes in the channel
        qotd                  Enables the question of the day to be sent to the res...
        removecensor          Remove censored words
        starboard_set         Set the channel for starboard
        welcome_setup         Set the channel for welcome messages
        wordcensor            Censors a word on the server""",

    "Music and Moderation commands": """
        Music bot commands, cause all the other bots are dying!

        disconnect            
        equalizer             
        now                   
        pause                 
        play                  
        queue                 
        remove                
        repeat                
        save                  
        seek                  
        shuffle               
        skip                  
        volume                

        Moderation Commands
        `kick`, `ban`, `mute`, `unmute`, `wordcensor`, `removecensor`, `prune`, `clean`, `warn`, `announce` 
        """,

    'Bot Commands': """
        `.advancedhelp`
        `.botinfo` – Bot stats.
        `.dev`
        `.invite`
        `.ping` – checks ping and latency
        `.suggestdev`
        `.vote`""",

    "Utility": """
        Useful stuff

        utilities Commands
        `.ascii`
        `.avatar`
        `.channelinfo` – Shows channel information
        `.choose` – Chooses between multiple choices.
        `.clap` – converts the message into :clap: claps :clap:
        `.convert` – Convert a video or audio file to anything you like
        `.covid` – Covid-19 Statistics for any countries
        `.define`
        `.embed` – Send complex rich embeds with this command!
        `.google` – Returns a google link for a query
        `.imagesearch` – Google image search. [p]i Lillie pokemon sun and moon
        `.joined` – Says when a member joined.
        `.lenny` – Lenny and tableflip group commands
        `.math`
        `.maxfont`
        `.members`
        `.meme` – get a random meme from reddit!
        `.morse`
        `.multi_choice` – creates a poll with multiple choices
        `.poll` – creates a poll with 2 choices
        `.randomimag`e – Get random images every time!
        `.rate` – Rates what you desire
        `.reverse` – !poow ,ffuts esreveR
        `.serverinfo` – Various info about the server. [p]help server for more info.
        `.spoiler`
        `.strikethrough`
        `.subreddit` – get a random post from any subreddit
        `.synonym`
        `.text_to_emoji` – why do you need an explaination to this, dumbo
        `.tinyurl` – Makes a link shorter using the tinyurl api
        `.translatef` – translates from french to english
        `.translateg` – translates from german to english
        `.ud` – Search terms with urbandictionary.com
        `.unmorse`
        `.whois` – gives info about member
        `.wiki` – Addictive Wikipedia results
        `.wolfram` – Ask Wolfram Alpha any question.
        `.wolframimage` – Ask Wolfram Alpha any question. Returns an image.
        `.wolframsolve` – Ask Wolfram Alpha any math question. Returns step by step answers.
        `names` - Generate a random name, last name or mash names together
        `qr` - A really really fancy QR code generator""",


    "Games and Miscellaneous": """
        .discomegle – Chat with other discord people anonymously! DM THIS TO THE BOT
        .space – Head command that contains commands about space.
        .typerace – Begin a typing race!
        .2048 – Play 2048 game
        .21dares – 21 truth or dare party game
        .connect4 – Connect4 for the boredom
        .hangman – Play Hangman
        .rps – Play Rock, Paper, Scissors game
        .tic – Starts a tic-tac-toe game with yourself.
        
        ***DISCORD TOGETHER GAMES***
        .betrayal_game – Play with friends only to be betrayed
        .chess – Play a game of chess
        .doodlecrew – Play a game of scribbl with your friends!
        .fishington – Go fishing in fishington
        .lettertile – Play a game of scramble with friends!
        .poker – Poker game
        .wordsnack – IM too dumb for this lmfao
        .youtube_together – Watch youtube together with your friends!""",

    "Image Commands": """
        Image Commands!!
        .achievement – Achievement unlocked
        .affect
        .amiajoke
        .bad
        .birb
        .calling – Call meme
        .captcha – Make a custom fake captcha!!
        .cat
        .catgirl
        .coffee
        .colourify
        .didumean
        .disfine
        .dog
        .drake
        .factimage – Make a custom fake fact image!!
        .filter – Deepfry avatar
        .floor
        .fml
        .imgur
        .kill
        .salty
        .scroll
        .shame
        .ship
        .textart – Generate cool font
        .wanted
        .what
        .invert - Inverts the colours of an image!"""

}
FACES = [
    "¢‿¢",
    "©¿© o",
    "ª{•̃̾_•̃̾}ª",
    "¬_¬",
    "¯＼(º_o)/¯",
    "¯\\(º o)/¯",
    "¯\\_(⊙︿⊙)_/¯",
    "¯\\_(ツ)_/¯",
    "°ω°",
    "°Д°",
    "°‿‿°",
    "°ﺑ°",
    "´ ▽ ` )ﾉ",
    "¿ⓧ_ⓧﮌ",
    "Ò,ó",
    "ó‿ó",
    "ô⌐ô",
    "ôヮô",
    "ŎםŎ",
    "ŏﺡó",
    "ʕ•̫͡•ʔ",
    "ʕ•ᴥ•ʔ",
    "ʘ‿ʘ",
    "˚•_•˚",
    "˚⌇˚",
    "˚▱˚",
    "̿ ̿̿'̿'\\̵͇̿̿\\=(•̪●)=/̵͇̿̿/'̿̿ ̿ ̿ ̿",
    "͡° ͜ʖ ͡°",
    "Σ ◕ ◡ ◕",
    "Σ (ﾟДﾟ;)",
    "Σ(ﾟДﾟ；≡；ﾟдﾟ)",
    "Σ(ﾟДﾟ )",
    "Σ(||ﾟДﾟ)",
    "Φ,Φ",
    "δﺡό",
    "σ_σ",
    "д_д",
    "ф_ф",
    "щ（ﾟДﾟщ）",
    "щ(ಠ益ಠщ)",
    "щ(ಥДಥщ)",
    "Ծ_Ծ",
    "أ‿أ",
    "ب_ب",
    "ح˚௰˚づ",
    "ح˚ᆺ˚ว",
    "حᇂﮌᇂ)",
    "٩๏̯͡๏۶",
    "٩๏̯͡๏)۶",
    "٩◔̯◔۶",
    "٩(×̯×)۶",
    "٩(̾●̮̮̃̾•̃̾)۶",
    "٩(͡๏̯͡๏)۶",
    "٩(͡๏̯ ͡๏)۶",
    "٩(ಥ_ಥ)۶",
    "٩(•̮̮̃•̃)۶",
    "٩(●̮̮̃•̃)۶",
    "٩(●̮̮̃●̃)۶",
    "٩(｡͡•‿•｡)۶",
    "٩(-̮̮̃•̃)۶",
    "٩(-̮̮̃-̃)۶",
    "۞_۞",
    "۞_۟۞",
    "۹ↁﮌↁ",
    "۹⌤_⌤۹",
    "॓_॔",
    "१✌◡✌५",
    "१|˚–˚|५",
    "ਉ_ਉ",
    "ଘ_ଘ",
    "இ_இ",
    "ఠ_ఠ",
    "రృర",
    "ಠ¿ಠi",
    "ಠ‿ಠ",
    "ಠ⌣ಠ",
    "ಠ╭╮ಠ",
    "ಠ▃ಠ",
    "ಠ◡ಠ",
    "ಠ益ಠ",
    "ಠ益ಠ",
    "ಠ︵ಠ凸",
    "ಠ , ಥ",
    "ಠ.ಠ",
    "ಠoಠ",
    "ಠ_ృ",
    "ಠ_ಠ",
    "ಠ_๏",
    "ಠ~ಠ",
    "ಡ_ಡ",
    "ತಎತ",
    "ತ_ತ",
    "ಥдಥ",
    "ಥ‿ಥ",
    "ಥ⌣ಥ",
    "ಥ◡ಥ",
    "ಥ﹏ಥ",
    "ಥ_ಥ",
    "ಭ_ಭ",
    "ರ_ರ",
    "ಸ , ໖",
    "ಸ_ಸ",
    "ക_ക",
    "อ้_อ้",
    "อ_อ",
    "โ๏௰๏ใ ื",
    "๏̯͡๏﴿",
    "๏̯͡๏",
    "๏̯͡๏﴿",
    "๏[-ิิ_•ิ]๏",
    "๏_๏",
    "໖_໖",
    "༺‿༻",
    "ლ(´ڡ`ლ)",
    "ლ(́◉◞౪◟◉‵ლ)",
    "ლ(ಠ益ಠლ)",
    "ლ(╹◡╹ლ)",
    "ლ(◉◞౪◟◉‵ლ)",
    "ლ,ᔑ•ﺪ͟͠•ᔐ.ლ",
    "ᄽὁȍ ̪ őὀᄿ",
    "ᕕ( ᐛ )ᕗ",
    "ᕙ(⇀‸↼‶)ᕗ",
    "ᕦ(ò_óˇ)ᕤ",
    "ᶘ ᵒᴥᵒᶅ",
    "‘︿’",
    "•▱•",
    "•✞_✞•",
    "•ﺑ•",
    "•(⌚_⌚)•",
    "•_•)",
    "‷̗ↂ凸ↂ‴̖",
    "‹•.•›",
    "‹› ‹(•¿•)› ‹›",
    "‹(ᵒᴥᵒ­­­­­)›",
    "‹(•¿•)›",
    "ↁ_ↁ",
    "⇎_⇎",
    "∩(︶▽︶)∩",
    "∩( ・ω・)∩",
    "≖‿≖",
    "≧ヮ≦",
    "⊂•⊃_⊂•⊃",
    "⊂⌒~⊃｡Д｡)⊃",
    "⊂(◉‿◉)つ",
    "⊂(ﾟДﾟ,,⊂⌒｀つ",
    "⊙ω⊙",
    "⊙▂⊙",
    "⊙▃⊙",
    "⊙△⊙",
    "⊙︿⊙",
    "⊙﹏⊙",
    "⊙０⊙",
    "⊛ठ̯⊛",
    "⋋ō_ō`",
    "━━━ヽ(ヽ(ﾟヽ(ﾟ∀ヽ(ﾟ∀ﾟヽ(ﾟ∀ﾟ)ﾉﾟ∀ﾟ)ﾉ∀ﾟ)ﾉﾟ)ﾉ)ﾉ━━━",
    "┌∩┐(◕_◕)┌∩┐",
    "┌( ಠ_ಠ)┘",
    "┌( ಥ_ಥ)┘",
    "╚(•⌂•)╝",
    "╭╮╭╮☜{•̃̾_•̃̾}☞╭╮╭╮",
    "╭✬⌢✬╮",
    "╮(─▽─)╭",
    "╯‵Д′)╯彡┻━┻",
    "╰☆╮",
    "□_□",
    "►_◄",
    "◃┆◉◡◉┆▷",
    "◉△◉",
    "◉︵◉",
    "◉_◉",
    "○_○",
    "●¿●\\ ~",
    "●_●",
    "◔̯◔",
    "◔ᴗ◔",
    "◔ ⌣ ◔",
    "◔_◔",
    "◕ω◕",
    "◕‿◕",
    "◕◡◕",
    "◕ ◡ ◕",
    "◖♪_♪|◗",
    "◖|◔◡◉|◗",
    "◘_◘",
    "◙‿◙",
    "◜㍕◝",
    "◪_◪",
    "◮_◮",
    "☁ ☝ˆ~ˆ☂",
    "☆¸☆",
    "☉‿⊙",
    "☉_☉",
    "☐_☐",
    "☜ق❂Ⴢ❂ق☞",
    "☜(⌒▽⌒)☞",
    "☜(ﾟヮﾟ☜)",
    "☜-(ΘLΘ)-☞",
    "☝☞✌",
    "☮▁▂▃▄☾ ♛ ◡ ♛ ☽▄▃▂▁☮",
    "☹_☹",
    "☻_☻",
    "☼.☼",
    "☾˙❀‿❀˙☽",
    "♀ح♀ヾ",
    "♥‿♥",
    "♥╣[-_-]╠♥",
    "♥╭╮♥",
    "♥◡♥",
    "✌♫♪˙❤‿❤˙♫♪✌",
    "✌.ʕʘ‿ʘʔ.✌",
    "✌.|•͡˘‿•͡˘|.✌",
    "✖‿✖",
    "✖_✖",
    "❐‿❑",
    "⨀_⨀",
    "⨀_Ꙩ",
    "⨂_⨂",
    "〆(・∀・＠)",
    "《〠_〠》",
    "【•】_【•】",
    "〠_〠",
    "〴⋋_⋌〵",
    "の� �の",
    "ニガー? ━━━━━━(ﾟ∀ﾟ)━━━━━━ ニガー?",
    "ペ㍕˚\\",
    "ヽ(´ｰ｀ )ﾉ",
    "ヽ(๏∀๏ )ﾉ",
    "ヽ(｀Д´)ﾉ",
    "ヽ(ｏ`皿′ｏ)ﾉ",
    "ヽ(`Д´)ﾉ",
    "ㅎ_ㅎ",
    "乂◜◬◝乂",
    "凸ಠ益ಠ)凸",
    "句_句",
    "Ꙩ⌵Ꙩ",
    "Ꙩ_Ꙩ",
    "ꙩ_ꙩ",
    "Ꙫ_Ꙫ",
    "ꙫ_ꙫ",
    "ꙮ_ꙮ",
    "흫_흫",
    "句_句",
    "﴾͡๏̯͡๏﴿ O'RLY?",
    "¯\\(ºдಠ)/¯",
    "（·×·）",
    "（⌒Д⌒）",
    "（╹ェ╹）",
    "（♯・∀・）⊃",
    "（　´∀｀）☆",
    "（　´∀｀）",
    "（゜Д゜）",
    "（・∀・）",
    "（・Ａ・）",
    "（ﾟ∀ﾟ）",
    "（￣へ￣）",
    "（ ´☣///_ゝ///☣｀）",
    "（ つ Д ｀）",
    "＿☆（ ´_⊃｀）☆＿",
    "｡◕‿‿◕｡",
    "｡◕ ‿ ◕｡",
    "!⑈ˆ~ˆ!⑈",
    "!(｀･ω･｡)",
    "(¬‿¬)",
    "(¬▂¬)",
    "(¬_¬)",
    "(°ℇ °)",
    "(°∀°)",
    "(´ω｀)",
    "(´◉◞౪◟◉)",
    "(´ヘ｀;)",
    "(´・ω・｀)",
    "(´ー｀)",
    "(ʘ‿ʘ)",
    "(ʘ_ʘ)",
    "(˚இ˚)",
    "(͡๏̯͡๏)",
    "(ΘεΘ;)",
    "(ι´Д｀)ﾉ",
    "(Ծ‸ Ծ)",
    "(॓_॔)",
    "(० ्०)",
    "(ு८ு_ .:)",
    "(ಠ‾ಠ)",
    "(ಠ‿ʘ)",
    "(ಠ‿ಠ)",
    "(ಠ⌣ಠ)",
    "(ಠ益ಠ ╬)",
    "(ಠ益ಠ)",
    "(ಠ_ృ)",
    "(ಠ_ಠ)",
    "(ಥ﹏ಥ)",
    "(ಥ_ಥ)",
    "(๏̯͡๏ )",
    "(ღ˘⌣˘ღ) ♫･*:.｡. .｡.:*･",
    "(ღ˘⌣˘ღ)",
    "(ᵔᴥᵔ)",
    "(•ω•)",
    "(•‿•)",
    "(•⊙ω⊙•)",
    "(• ε •)",
    "(∩▂∩)",
    "(∩︵∩)",
    "(∪ ◡ ∪)",
    "(≧ω≦)",
    "(≧◡≦)",
    "(≧ロ≦)",
    "(⊙ヮ⊙)",
    "(⊙_◎)",
    "(⋋▂⋌)",
    "(⌐■_■)",
    "(─‿‿─)",
    "(┛◉Д◉)┛┻━┻",
    "(╥_╥)",
    "(╬ಠ益ಠ)",
    "(╬◣д◢)",
    "(╬ ಠ益ಠ)",
    "(╯°□°）╯︵ ┻━┻",
    "(╯ಊ╰)",
    "(╯◕_◕)╯",
    "(╯︵╰,)",
    "(╯3╰)",
    "(╯_╰)",
    "(╹◡╹)凸",
    "(▰˘◡˘▰)",
    "(●´ω｀●)",
    "(●´∀｀●)",
    "(◑‿◐)",
    "(◑◡◑)",
    "(◕‿◕✿)",
    "(◕‿◕)",
    "(◕‿-)",
    "(◕︵◕)",
    "(◕ ^ ◕)",
    "(◕_◕)",
    "(◜௰◝)",
    "(◡‿◡✿)",
    "(◣_◢)",
    "(☞ﾟ∀ﾟ)☞",
    "(☞ﾟヮﾟ)☞",
    "(☞ﾟ ∀ﾟ )☞",
    "(☼◡☼)",
    "(☼_☼)",
    "(✌ﾟ∀ﾟ)☞",
    "(✖╭╮✖)",
    "(✪㉨✪)",
    "(✿◠‿◠)",
    "(✿ ♥‿♥)",
    "(　・∀・)",
    "(　･ัω･ั)？",
    "(　ﾟ∀ﾟ)o彡゜えーりんえーりん!!",
    "(。・_・。)",
    "(つд｀)",
    "(づ｡◕‿‿◕｡)づ",
    "(ノಠ益ಠ)ノ彡┻━┻",
    "(ノ ◑‿◑)ノ",
    "(ノ_・。)",
    "(・∀・ )",
    "(屮ﾟДﾟ)屮",
    "(︶ω︶)",
    "(︶︹︺)",
    "(ﺧ益ﺨ)",
    "(；一_一)",
    "(｀・ω・´)”",
    "(｡◕‿‿◕｡)",
    "(｡◕‿◕｡)",
    "(｡◕ ‿ ◕｡)",
    "(｡♥‿♥｡)",
    "(｡･ω..･)っ",
    "(･ｪ-)",
    "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
    "(ﾟДﾟ)",
    "(ﾟДﾟ)y─┛~~",
    "(ﾟ∀ﾟ)",
    "(ﾟヮﾟ)",
    "(￣□￣)",
    "(￣。￣)",
    "(￣ー￣)",
    "(￣(エ)￣)",
    "( °٢° )",
    "( ´_ゝ｀)",
    "( ͡° ͜ʖ ͡°)",
    "( ͡~ ͜ʖ ͡°)",
    "( ಠ◡ಠ )",
    "( •_•)>⌐■-■",
    "( 　ﾟ,_ゝﾟ)",
    "( ･ิз･ิ)",
    "( ﾟдﾟ)､",
    "( ^▽^)σ)~O~)",
    "((((゜д゜;))))",
    "(*´д｀*)",
    "(*..Д｀)",
    "(*..д｀*)",
    "(*~▽~)",
    "(-’๏_๏’-)",
    "(-＿- )ノ",
    "(/◔ ◡ ◔)/",
    "(///_ಥ)",
    "(;´Д`)",
    "(=ω=;)",
    "(=゜ω゜)",
    "(>'o')>♥<('o'<)",
    "(n˘v˘•)¬",
    "(o´ω｀o)",
    "(V)(°,,°)(V)",
    "(\/) (°,,°) (\/) WOOPwoopwowopwoopwoopwoop!",
    "(^▽^)",
    "(`･ω･´)",
    "(~￣▽￣)~",
    "/╲/\\╭ºoꍘoº╮/\\╱\\",
    "<【☯】‿【☯】>",
    "= (ﾟдﾟ)ｳ",
    "@_@",
    "d(*⌒▽⌒*)b",
    "o(≧∀≦)o",
    "o(≧o≦)o",
    "q(❂‿❂)p",
    "y=ｰ( ﾟдﾟ)･∵.",
    "\\˚ㄥ˚\\",
    "\\ᇂ_ᇂ\\",
    "\\(ಠ ὡ ಠ )/",
    "\\(◕ ◡ ◕\\)",
    "^̮^",
    "^ㅂ^",
    "_(͡๏̯͡๏)_",
    "{´◕ ◡ ◕｀}",
    "{ಠ_ಠ}__,,|,",
    "{◕ ◡ ◕}",
]


def Help_Embed():
    em = discord.Embed(title='🔴 ***SPACEBOT HELP***',
                       description=f"""
        > I'm a feature-packed bot with tons of commands.
        > Spacebot is one of the best multipurpose bots with
        > Fun, Utility, Games, Music, Moderation and Levelling!
    
        ⚠️ *What's new??* - MUSIC OVERHAUL AND OPEN SOURCE!!!
        > Load balancing has been implemented to music. 
        > This means that Spacebot will get your server's registered location and play music in the same country!

        > FILTERS - as of right now, there is bassboost, treble, jazz, pop filters. 
            There will be more, but i need a music enthusiast cause i dont understand this

        > SPACEBOT IS NOW OPEN SOURCE!! if you know a little bit of python, consider contributing or just 
        ⭐ this project! https://github.com/dhravya/spacebot-discord

        Just click on this link to enable Slash commands!! (dsc.gg/spacebt)[https://dsc.gg/spacebt]
        > You can also use the command `.help` to get the help menu.

        ```Invite me using the .invite command!```
        """)
    em.set_image(
        url='https://images-ext-2.discordapp.net/external/MWmqAGeEWIpEaaq9rcMCrPYzMEScRGxEOB4ao9Ph2s0/https/media.discordapp.net/attachments/888798533459775491/903219469650890862/standard.gif')
    em.set_footer(
        text="Check out https://millenia.tech !!")
    em.color = discord.Colour.blue()
    return em
