
import datetime
import emoji
import fbchat
import getch
import magic
import os
import sys
import urllib.request
from address_book import *
from ask_question import *
from autocomplete import *
from getpass import getpass
from fbchat.models import *
from functools import reduce


class reactEmoji(object):
    def __init__(self, reaction):
        self.value = reaction


class Messenger_CLI:

    def __init__(self, client, receive):
        self.client = client
        self.address_book = Address_Book()
        self.locked = False
        self.friend = None
        self.uid = None
        self.message = None
        self.iterations = 1
        self.send = lambda msg, emoji, uid: \
                    self.client.send(Message(text=msg, emoji_size=emoji), uid)
        self.args = [None, None, None] #msg, emoji, uid
        self.receive = receive


    def run(self):
        while True:
            if not self.locked:
                self.__get_friend(True)

            self.__get_message()
            self.__send_message()
            self.__reset()


    def __autocomplete_friend(self):
        commands = ["--delete", "--quit", "--view"]
        contacts = self.address_book.get_contacts() + commands

        old_delims = readline.get_completer_delims()
        readline.set_completer_delims(old_delims.replace('-', ''))

        completer = MyCompleter(contacts, True)
        readline.set_completer(completer.complete)
        readline.parse_and_bind('tab: complete')
        friend = input("Friend: ")

        return friend


    def __handle_friend_commands(self, friend):
        if friend == "--quit":
            self.client.logout()
            exit(0)
        if friend == "--view":
            self.address_book.view_contacts()
            self.run()

        pattern = re.compile("--delete (.+)") #--delete [some text]
        if pattern.match(friend):
            contact = pattern.search(friend).group(1)
            self.address_book.remove_contact(contact)
            self.run()


    def __get_friend(self, first_time, friend=None):
        if first_time:
            friend = self.__autocomplete_friend()
            
        self.__handle_friend_commands(friend)

        if self.address_book.contact_exists(friend):
            self.friend = friend
            self.uid = self.address_book.get_uid(friend)
        else:
            recipient = self.__get_recipient(friend)
            if recipient == None:
                return

            message = "Name is not in address book. Do you wish to send a message to " \
                    + recipient.name +"? (Y/n) "
            fail_message = "Please enter a valid response: "
            ok_response = lambda x, _: x not in ["Y", "n"]

            if ask_question(message, fail_message, ok_response) == "Y":
                self.address_book.add_contact(recipient)
            else:
                return self.__get_friend(True)

            self.friend = recipient.name
            self.uid = recipient.uid


    def __get_recipient(self, friend):
        try:
            return self.client.searchForUsers(friend)[0]
        except:
            new_friend = input("Could not find friend.  Please enter different name: ")
            self.__get_friend(False, new_friend)


    def __autocomplete(self):
        EMOJIS = [':smile:', ':laughing:', ':blush:', ':smiley:', ':relaxed:', ':smirk:', ':heart_eyes:', ':kissing_heart:', ':kissing_closed_eyes:', ':flushed:', ':relieved:', ':satisfied:', ':grin:', ':wink:', ':stuck_out_tongue_winking_eye:', ':stuck_out_tongue_closed_eyes:', ':grinning:', ':kissing:', ':kissing_smiling_eyes:', ':stuck_out_tongue:', ':sleeping:  ', ':worried:', ':frowning:', ':anguished:', ':open_mouth:', ':grimacing:', ':confused:', ':hushed:', ':expressionless:', ':unamused:', ':sweat_smile:', ':sweat:', ':disappointed_relieved:', ':weary:', ':pensive:', ':disappointed:', ':confounded:', ':fearful:', ':cold_sweat:', ':persevere:', ':cry:', ':sob:', ':joy:', ':astonished:', ':scream:', ':tired_face:', ':angry:', ':rage:', ':triumph:', ':sleepy:', ':yum:', ':mask:', ':sunglasses:', ':dizzy_face:', ':imp:', ':smiling_imp:', ':neutral_face:', ':no_mouth:', ':innocent:', ':alien:', ':yellow_heart:', ':blue_heart:', ':purple_heart:', ':heart:', ':green_heart:', ':broken_heart:', ':heartbeat:', ':heartpulse:', ':two_hearts:', ':revolving_hearts:', ':cupid:', ':sparkling_heart:', ':sparkles:', ':star:', ':star2:', ':dizzy:', ':boom:', ':collision:', ':anger:', ':exclamation:', ':question:', ':grey_exclamation:', ':grey_question:', ':zzz:', ':dash:', ':sweat_drops:', ':notes:', ':musical_note:', ':fire:', ':hankey:', ':poop:', ':shit:', ':+1:', ':thumbsup:', ':-1:', ':thumbsdown:', ':ok_hand:', ':punch:', ':facepunch:', ':fist:', ':v:', ':wave:', ':hand:', ':raised_hand:', ':open_hands:', ':point_up:', ':point_down:', ':point_left:', ':point_right:', ':raised_hands:', ':pray:', ':point_up_2:', ':clap:', ':muscle:', ':runner:', ':running:', ':couple:', ':family:', ':two_men_holding_hands:', ':two_women_holding_hands:', ':dancer:', ':dancers:', ':ok_woman:', ':no_good:', ':information_desk_person:', ':raising_hand:', ':bride_with_veil:', ':person_with_pouting_face:', ':person_frowning:', ':bow:', ':couplekiss:', ':couple_with_heart:', ':massage:', ':haircut:', ':nail_care:', ':boy:', ':girl:', ':woman:', ':man:', ':baby:', ':older_woman:', ':older_man:', ':person_with_blond_hair:', ':man_with_gua_pi_mao:', ':man_with_turban:', ':construction_worker:', ':cop:', ':angel:', ':princess:', ':smiley_cat:', ':smile_cat:', ':heart_eyes_cat:', ':kissing_cat:', ':smirk_cat:', ':scream_cat:', ':crying_cat_face:', ':joy_cat:', ':pouting_cat:', ':japanese_ogre:', ':japanese_goblin:', ':see_no_evil:', ':hear_no_evil:', ':speak_no_evil:', ':guardsman:', ':skull:', ':feet:', ':lips:', ':kiss:', ':droplet:', ':ear:', ':eyes:', ':nose:', ':tongue:', ':love_letter:', ':bust_in_silhouette:', ':busts_in_silhouette:', ':speech_balloon:', ':thought_balloon:', ':sunny:', ':umbrella:', ':cloud:', ':snowflake:', ':snowman:', ':zap:', ':cyclone:', ':foggy:', ':ocean:', ':cat:', ':dog:', ':mouse:', ':hamster:', ':rabbit:', ':wolf:', ':frog:', ':tiger:', ':koala:', ':bear:', ':pig:', ':pig_nose:', ':cow:', ':boar:', ':monkey_face:', ':monkey:', ':horse:', ':racehorse:', ':camel:', ':sheep:', ':elephant:', ':panda_face:', ':snake:', ':bird:', ':baby_chick:', ':hatched_chick:', ':hatching_chick:', ':chicken:', ':penguin:', ':turtle:', ':bug:', ':honeybee:', ':ant:', ':beetle:', ':snail:', ':octopus:', ':tropical_fish:', ':fish:', ':whale:', ':whale2:', ':dolphin:', ':cow2:', ':ram:', ':rat:', ':water_buffalo:', ':tiger2:', ':rabbit2:', ':dragon:', ':goat:', ':rooster:', ':dog2:', ':pig2:', ':mouse2:', ':ox:', ':dragon_face:', ':blowfish:', ':crocodile:', ':dromedary_camel:', ':leopard:', ':cat2:', ':poodle:', ':paw_prints:', ':bouquet:', ':cherry_blossom:', ':tulip:', ':four_leaf_clover:', ':rose:', ':sunflower:', ':hibiscus:', ':maple_leaf:', ':leaves:', ':fallen_leaf:', ':herb:', ':mushroom:', ':cactus:', ':palm_tree:', ':evergreen_tree:', ':deciduous_tree:', ':chestnut:', ':seedling:', ':blossom:', ':ear_of_rice:', ':shell:', ':globe_with_meridians:', ':sun_with_face:', ':full_moon_with_face:', ':new_moon_with_face:', ':new_moon:', ':waxing_crescent_moon:', ':first_quarter_moon:', ':waxing_gibbous_moon:', ':full_moon:', ':waning_gibbous_moon:', ':last_quarter_moon:', ':waning_crescent_moon:', ':last_quarter_moon_with_face:', ':first_quarter_moon_with_face:', ':crescent_moon:', ':earth_africa:', ':earth_americas:', ':earth_asia:', ':volcano:', ':milky_way:', ':partly_sunny:', ':bamboo:', ':gift_heart:', ':dolls:', ':school_satchel:', ':mortar_board:', ':flags:', ':fireworks:', ':sparkler:', ':wind_chime:', ':rice_scene:', ':jack_o_lantern:', ':ghost:', ':santa:', ':christmas_tree:', ':gift:', ':bell:', ':no_bell:', ':tanabata_tree:', ':tada:', ':confetti_ball:', ':balloon:', ':crystal_ball:', ':cd:', ':dvd:', ':floppy_disk:', ':camera:', ':video_camera:', ':movie_camera:', ':computer:', ':tv:', ':iphone:', ':phone:', ':telephone:', ':telephone_receiver:', ':pager:', ':fax:', ':minidisc:', ':vhs:', ':sound:', ':speaker:', ':mute:', ':loudspeaker:', ':mega:', ':hourglass:', ':hourglass_flowing_sand:', ':alarm_clock:', ':watch:', ':radio:', ':satellite:', ':loop:', ':mag:', ':mag_right:', ':unlock:', ':lock:', ':lock_with_ink_pen:', ':closed_lock_with_key:', ':key:', ':bulb:', ':flashlight:', ':high_brightness:', ':low_brightness:', ':electric_plug:', ':battery:', ':calling:', ':email:', ':mailbox:', ':postbox:', ':bath:', ':bathtub:', ':shower:', ':toilet:', ':wrench:', ':nut_and_bolt:', ':hammer:', ':seat:', ':moneybag:', ':yen:', ':dollar:', ':pound:', ':euro:', ':credit_card:', ':money_with_wings:', ':e-mail:', ':inbox_tray:', ':outbox_tray:', ':envelope:', ':incoming_envelope:', ':postal_horn:', ':mailbox_closed:', ':mailbox_with_mail:', ':mailbox_with_no_mail:', ':package:', ':door:', ':smoking:', ':bomb:', ':gun:', ':hocho:', ':pill:', ':syringe:', ':page_facing_up:', ':page_with_curl:', ':bookmark_tabs:', ':bar_chart:', ':chart_with_upwards_trend:', ':chart_with_downwards_trend:', ':scroll:', ':clipboard:', ':calendar:', ':date:', ':card_index:', ':file_folder:', ':open_file_folder:', ':scissors:', ':pushpin:', ':paperclip:', ':black_nib:', ':pencil2:', ':straight_ruler:', ':triangular_ruler:', ':closed_book:', ':green_book:', ':blue_book:', ':orange_book:', ':notebook:', ':notebook_with_decorative_cover:', ':ledger:', ':books:', ':bookmark:', ':name_badge:', ':microscope:', ':telescope:', ':newspaper:', ':football:', ':basketball:', ':soccer:', ':baseball:', ':tennis:', ':8ball:', ':rugby_football:', ':bowling:', ':golf:', ':mountain_bicyclist:', ':bicyclist:', ':horse_racing:', ':snowboarder:', ':swimmer:', ':surfer:', ':ski:', ':spades:', ':hearts:', ':clubs:', ':diamonds:', ':gem:', ':ring:', ':trophy:', ':musical_score:', ':musical_keyboard:', ':violin:', ':space_invader:', ':video_game:', ':black_joker:', ':flower_playing_cards:', ':game_die:', ':dart:', ':mahjong:', ':clapper:', ':memo:', ':pencil:', ':book:', ':art:', ':microphone:', ':headphones:', ':trumpet:', ':saxophone:', ':guitar:', ':shoe:', ':sandal:', ':high_heel:', ':lipstick:', ':boot:', ':shirt:', ':tshirt:', ':necktie:', ':womans_clothes:', ':dress:', ':running_shirt_with_sash:', ':jeans:', ':kimono:', ':bikini:', ':ribbon:', ':tophat:', ':crown:', ':womans_hat:', ':mans_shoe:', ':closed_umbrella:', ':briefcase:', ':handbag:', ':pouch:', ':purse:', ':eyeglasses:', ':fishing_pole_and_fish:', ':coffee:', ':tea:', ':sake:', ':baby_bottle:', ':beer:', ':beers:', ':cocktail:', ':tropical_drink:', ':wine_glass:', ':fork_and_knife:', ':pizza:', ':hamburger:', ':fries:', ':poultry_leg:', ':meat_on_bone:', ':spaghetti:', ':curry:', ':fried_shrimp:', ':bento:', ':sushi:', ':fish_cake:', ':rice_ball:', ':rice_cracker:', ':rice:', ':ramen:', ':stew:', ':oden:', ':dango:', ':egg:', ':bread:', ':doughnut:', ':custard:', ':icecream:', ':ice_cream:', ':shaved_ice:', ':birthday:', ':cake:', ':cookie:', ':chocolate_bar:', ':candy:', ':lollipop:', ':honey_pot:', ':apple:', ':green_apple:', ':tangerine:', ':lemon:', ':cherries:', ':grapes:', ':watermelon:', ':strawberry:', ':peach:', ':melon:', ':banana:', ':pear:', ':pineapple:', ':sweet_potato:', ':eggplant:', ':tomato:', ':corn:', ':house:', ':house_with_garden:', ':school:', ':office:', ':post_office:', ':hospital:', ':bank:', ':convenience_store:', ':love_hotel:', ':hotel:', ':wedding:', ':church:', ':department_store:', ':european_post_office:', ':city_sunrise:', ':city_sunset:', ':japanese_castle:', ':european_castle:', ':tent:', ':factory:', ':tokyo_tower:', ':japan:', ':mount_fuji:', ':sunrise_over_mountains:', ':sunrise:', ':stars:', ':statue_of_liberty:', ':bridge_at_night:', ':carousel_horse:', ':rainbow:', ':ferris_wheel:', ':fountain:', ':roller_coaster:', ':ship:', ':speedboat:', ':boat:', ':sailboat:', ':rowboat:', ':anchor:', ':rocket:', ':airplane:', ':helicopter:', ':steam_locomotive:', ':tram:', ':mountain_railway:', ':bike:', ':aerial_tramway:', ':suspension_railway:', ':mountain_cableway:', ':tractor:', ':blue_car:', ':oncoming_automobile:', ':car:', ':red_car:', ':taxi:', ':oncoming_taxi:', ':articulated_lorry:', ':bus:', ':oncoming_bus:', ':rotating_light:', ':police_car:', ':oncoming_police_car:', ':fire_engine:', ':ambulance:', ':minibus:', ':truck:', ':train:', ':station:', ':train2:', ':bullettrain_front:', ':bullettrain_side:', ':light_rail:', ':monorail:', ':railway_car:', ':trolleybus:', ':ticket:', ':fuelpump:', ':vertical_traffic_light:', ':traffic_light:', ':warning:', ':construction:', ':beginner:', ':atm:', ':slot_machine:', ':busstop:', ':barber:', ':hotsprings:', ':checkered_flag:', ':crossed_flags:', ':izakaya_lantern:', ':moyai:', ':circus_tent:', ':performing_arts:', ':round_pushpin:', ':triangular_flag_on_post:', ':keycap_ten:', ':1234:', ':symbols:', ':arrow_backward:', ':arrow_down:', ':arrow_forward:', ':arrow_left:', ':capital_abcd:', ':abcd:', ':abc:', ':arrow_lower_left:', ':arrow_lower_right:', ':arrow_right:', ':arrow_up:', ':arrow_upper_left:', ':arrow_upper_right:', ':arrow_double_down:', ':arrow_double_up:', ':arrow_down_small:', ':arrow_heading_down:', ':arrow_heading_up:', ':leftwards_arrow_with_hook:', ':arrow_right_hook:', ':left_right_arrow:', ':arrow_up_down:', ':arrow_up_small:', ':arrows_clockwise:', ':arrows_counterclockwise:', ':rewind:', ':fast_forward:', ':information_source:', ':ok:', ':twisted_rightwards_arrows:', ':repeat:', ':repeat_one:', ':new:', ':top:', ':up:', ':cool:', ':free:', ':ng:', ':cinema:', ':koko:', ':signal_strength:', ':u5272:', ':u5408:', ':u55b6:', ':u6307:', ':u6708:', ':u6709:', ':u6e80:', ':u7121:', ':u7533:', ':u7a7a:', ':u7981:', ':sa:', ':restroom:', ':mens:', ':womens:', ':baby_symbol:', ':no_smoking:', ':parking:', ':wheelchair:', ':metro:', ':baggage_claim:', ':accept:', ':wc:', ':potable_water:', ':put_litter_in_its_place:', ':secret:', ':congratulations:', ':m:', ':passport_control:', ':left_luggage:', ':customs:', ':ideograph_advantage:', ':cl:', ':sos:', ':id:', ':no_entry_sign:', ':underage:', ':no_mobile_phones:', ':do_not_litter:', ':non-potable_water:', ':no_bicycles:', ':no_pedestrians:', ':children_crossing:', ':no_entry:', ':eight_spoked_asterisk:', ':sparkle:', ':eight_pointed_black_star:', ':heart_decoration:', ':vs:', ':vibration_mode:', ':mobile_phone_off:', ':chart:', ':currency_exchange:', ':aries:', ':taurus:', ':gemini:', ':cancer:', ':leo:', ':virgo:', ':libra:', ':scorpius:', ':sagittarius:', ':capricorn:', ':aquarius:', ':pisces:', ':ophiuchus:', ':six_pointed_star:', ':negative_squared_cross_mark:', ':a:', ':b:', ':ab:', ':o2:', ':diamond_shape_with_a_dot_inside:', ':recycle:', ':end:', ':back:', ':on:', ':soon:', ':clock1:', ':clock130:', ':clock10:', ':clock1030:', ':clock11:', ':clock1130:', ':clock12:', ':clock1230:', ':clock2:', ':clock230:', ':clock3:', ':clock330:', ':clock4:', ':clock430:', ':clock5:', ':clock530:', ':clock6:', ':clock630:', ':clock7:', ':clock730:', ':clock8:', ':clock830:', ':clock9:', ':clock930:', ':heavy_dollar_sign:', ':copyright:', ':registered:', ':tm:', ':x:', ':heavy_exclamation_mark:', ':bangbang:', ':interrobang:', ':o:', ':heavy_multiplication_x:', ':heavy_plus_sign:', ':heavy_minus_sign:', ':heavy_division_sign:', ':white_flower:', ':100:', ':heavy_check_mark:', ':ballot_box_with_check:', ':radio_button:', ':link:', ':curly_loop:', ':wavy_dash:', ':part_alternation_mark:', ':trident:', ':black_small_square:', ':white_small_square:', ':black_medium_small_square:', ':white_medium_small_square:', ':black_medium_square:', ':white_medium_square:', ':black_large_square:', ':white_large_square:', ':white_check_mark:', ':black_square_button:', ':white_square_button:', ':black_circle:', ':white_circle:', ':red_circle:', ':large_blue_circle:', ':large_blue_diamond:', ':large_orange_diamond:', ':small_blue_diamond:', ':small_orange_diamond:', ':small_red_triangle:', ':small_red_triangle_down:']

        old_delims = readline.get_completer_delims()
        readline.set_completer_delims(old_delims.replace(':', ''))

        completer = MyCompleter(EMOJIS)
        readline.set_completer(completer.complete)
        readline.parse_and_bind('tab: complete')
        text = input("Message text: ")

        return text


    def __scroll(self, intro, options):
        index = 1
        sys.stdout.write("\r" + "\033[K" + intro + options[index])

        key = getch.getch()

        # the left and right arrow keys are composed of three characters:
        # '\x1b', '[', and 'D' for the left key and '\x1b', '[', and 'C' for
        # the right key
        while ord(key) != 10: #enter
            if ord(key) == 27: #'\x1b'
                key = getch.getch()
                if ord(key) == 91: #'['
                    key = getch.getch()
                    if ord(key) == 68: #'D' left-arrow key
                        num_chars = len(options[index])
                        index = (index - 1) % len(options)
                        sys.stdout.write("\r" + "\033[K" + intro + options[index])
                    elif ord(key) == 67: #'C' right-arrow key
                        num_chars = len(options[index])
                        index = (index + 1) % len(options)
                        sys.stdout.write("\r" + "\033[K" + intro + options[index])
                        
            key = getch.getch()
            continue
        sys.stdout.write("\n")

        return index

    def __emoji(self, text):
        if text != "":
            return text
        intro = "Select the desired emoji size or \"none\" to not send the message: "
        index = self.__scroll(intro, ["none", "small", "medium", "large"])

        if index == 1:
            self.args[1] = EmojiSize.SMALL
        elif index == 2:
            self.args[1] = EmojiSize.MEDIUM
        elif index == 3:
            self.args[1] = EmojiSize.LARGE
        else:
            self.__reset
            self.run()

        chat_emoji = self.client.fetchThreadInfo(self.uid)[self.uid].emoji
        if chat_emoji:
            return chat_emoji
        else:
            return ""

    def __iterations(self, text):
        pattern = re.compile("^-i ([0-9]*[1-9][0-9]*) ([^\s].*)$") #-i [positive integer] [some_text]
        if pattern.match(text):
            self.iterations = int(pattern.search(text).group(1))
            text = pattern.search(text).group(2)

        return text


    def __spaces(self, text):
        pattern = re.compile("^-s ([^\s].*)$") #-s [some text]
        if pattern.match(text):
            as_list = list(pattern.search(text).group(1))
            no_spaces = filter(lambda x: x != " ", as_list)
            text = reduce(lambda acc,x: acc+x+" ", no_spaces, "")

        return text


    def __oboi(self, text):
        if text == "oboi":
            self.send = lambda img, uid: self.client.sendLocalImage(img, thread_id=uid)
            self.args = ['images/oboi.jpg', None, self.uid]


    def __contains_word(self, s, w):
        if s.startswith(w + ' ') or s == w:
            return len(w)
        elif s.find(' ' + w + ' ') != -1:
            return s.find(' ' + w + ' ') + len(w) + 1
        elif s.endswith(' ' + w):
            return s.find(' ' + w) + len(w) + 1
        else:
            return -1

    def __replace_word(self, text, find, replace):
        match = self.__contains_word(text, find)
        while match != -1:
            text = text[:match].replace(find, replace, 1) + text[match:]
            match = self.__contains_word(text, find)

        return text

    def __quit(self, text):
        if text == "--quit":
            self.__reset()
            self.run()


    def __print_arrows(self, author, i):
        OKGREEN = '\033[92m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'

        if author == self.client.uid:
            sys.stdout.write('[' + str(i) + '] ' + FAIL + "<-- " + ENDC)
        else:
            sys.stdout.write('[' + str(i) + '] ' + OKGREEN + "--> " + ENDC)


    def __display_messages(self, limit):
        messages = self.receive.fetchThreadMessages(self.uid, limit=limit)

        messages = messages[::-1]
        sys.stdout.write("\033[H\033[J") # clears screen

        num_to_id = dict()

        num_to_display = -1
        for i in range(len(messages)):
            num_to_display += 1
            self.__print_arrows(messages[i].author, num_to_display)
            num_to_id[i] = messages[i].uid
            if messages[i].text != "" and messages[i].text != None:
                print(messages[i].text)
            else:
                OKBLUE = '\033[94m'
                ENDC = '\033[0m'
                if messages[i].attachments != []:
                    print(OKBLUE + "Attachment" + ENDC)
                elif messages[i].sticker != None:
                    print(OKBLUE + "Sticker" + ENDC)
                else:
                    sys.stdout.write("\r" + "\033[K") # Clears current line
                    print(OKBLUE + "Messenger action" + ENDC)
                    num_to_display -= 1
                    messages[i] = None

        return list(filter(lambda x: x, messages))


    def __open_attachment(self, messages, msg_num):
        msg = messages[msg_num]
        if msg.attachments == []:
            print("Selected message contains no attachment")
            return

        abspath = (os.path.abspath(__file__))
        dname = os.path.dirname(abspath)
        os.chdir(dname)

        if not os.path.isdir("../downloads"):
            os.system("mkdir ../downloads")

        for i in range(len(msg.attachments)):
            img_url = self.client.fetchImageUrl(msg.attachments[i].uid)
            filename = "{:%Y%m%d-%H%M%S}-{}".format(datetime.datetime.now(),i)
            urllib.request.urlretrieve(img_url, "../downloads/"+filename)
            mime = magic.Magic(mime=True)
            ext = mime.from_file("../downloads/"+filename)
            ext = ext.split("/")[1]
            os.system("mv ../downloads/{} ../downloads/{}.{}"\
                                               .format(filename, filename, ext))
            os.system("open ../downloads/{}.{}".format(filename, ext))


    def __react(self, message_id):
        chat_emoji = self.client.fetchThreadInfo(self.uid)[self.uid].emoji
        reacts = ["none", '😍', '😆', '😮', '😢', '😠', '👍', '👎']
        if chat_emoji != None and chat_emoji not in reacts:
            reacts += [chat_emoji]

        intro = "Select the emoji with which you would like to react or \"none\" to not react at all: "
        index = self.__scroll(intro, reacts)
        if index == 0:
            self.__reset()
            self.run()
        reaction = reacts[index]
        
        try:
            self.client.reactToMessage(message_id, reactEmoji(reaction))
            print("Reaction successful")
        except:
            print("Reaction unsuccessful")


    def __log(self, text):
        pattern = re.compile("--log( ([0-9]*[1-9][0-9]*))?") #--log [positive integer] (" "[positive integer] is optional)
        if pattern.match(text):
            limit = pattern.search(text).group(2)
            limit = int(limit) if limit else 10
        else:
            return

        messages = self.__display_messages(limit)

        message = "React to a message by entering the message number.  Open an attachment using the --open command, followed by a space, and the number that corresponds attachment message.  Press 'q' to return. "
        fail_message = "Please enter a valid response: "
        extras = (limit, len(messages))

        result = ask_question(message, fail_message, check_response, extras)
        
        if result != "q":
            if result[:6] == "--open":
                self.__open_attachment(messages, int(result[7:]))
            else:
                message_id = messages[int(result)].uid
                self.__react(message_id)

        self.run()


    def __get_text(self):
        text = self.__autocomplete()
        self.__quit(text)
        text = emoji.emojize(text, use_aliases=True)
        text = self.__iterations(text)
        text = self.__spaces(text)
        text = self.__replace_word(text, "shru.gg", "¯\_(ツ)_/¯")
        self.__log(text)
        text = self.__emoji(text)
        self.args = [text, self.args[1], self.uid]
        self.__oboi(text)
        
        return text


    def __get_message(self):
        text = self.__get_text()

        if not self.locked and text == "--lock":
            self.locked = True
            print("Locked on " + self.friend)
            return self.__get_message()
        if self.locked and text == "--unlock":
            self.locked = False
            print("Unlocked from " + self.friend)
            self.__reset()
            self.run()

        self.message = text.rstrip()



    def __send_message(self):
        sent = False
        try:
            for _ in range(self.iterations):
                self.send(self.args[0], self.args[1], self.args[2])
                sent = True
        except:
            print("Not all messages sent" if sent else "Message not sent")

        if not self.locked:
            print("Message sent" if self.iterations == 1 else "Messages sent")


    def __reset(self):
        if not self.locked:
            self.friend = None
            self.uid = None
        self.message = None
        self.iterations = 1
        self.send = \
            lambda msg, emoji, uid: \
                    self.client.send(Message(text=msg, emoji_size=emoji), uid)
        self.args[1] = None


        


