#!/usr/bin/python
" seeing if I can still use Python for CGI scripts "
# with help from JamesTheAwesomeDud
# ref. https://stackoverflow.com/a/76159280
# note, to write to an sqlite3 database, the www-data user needs
#  write permissiong to the file AND to the directory

# import cgi # removed in Python 3.13
import cgitb
import email.parser
import email.policy
import urllib
import os
import sys
import time
import sqlite3

#print("Content-Type: text/html")
# print()
cgitb.enable()  # dump errors to stdout

# start and end of window of time for signups
OPEN_TIME = "2024-01-02 17:00"
CLOSED_TIME = "2024-01-08 17:00"

COUNTRIES_DROPDOWN = """
<select name="Country" id="Country" required>
<option value="" label="Select a country ... " selected="selected">Select a country ... </option>
<optgroup id="country-optgroup-Primary" label="Anglosphere favourtism">
<option value="US" label="United States">United States</option>
<option value="GB" label="Great Britain">Great Britain</option>
<option value="CA" label="Canada">Canada</option>
<option value="AU" label="Australia">Australia</option>
<option value="IE" label="Ireland">Ireland</option>
<option value="NZ" label="New Zealand">New Zealand</option>
<option value="SG" label="Singapore">Singapore</option>
</optgroup>
<optgroup id="country-optgroup-Huge" label="Huge. Huge!">
<option value="CN" label="China">China</option>
<option value="IN" label="India">India</option>
<option value="US" label="United States">United States</option>
<option value="ID" label="Indonesia">Indonesia</option>
<option value="PK" label="Pakistan">Pakistan</option>
<option value="NG" label="Nigeria">Nigeria</option>
<option value="BR" label="Brazil">Brazil</option>
<option value="BD" label="Bangladesh">Bangladesh</option>
<option value="RU" label="Russia">Russia</option>
<option value="MX" label="Mexico">Mexico</option>
<option value="PH" label="Philippines">Philippines</option>
<option value="EG" label="Egypt">Egypt</option>
<option value="DE" label="Germany">Germany</option>
<option value="TR" label="Turkey">Turkey</option>
<option value="FR" label="France">France</option>
<option value="GB" label="United Kingdom">United Kingdom</option>
<option value="TH" label="Thailand">Thailand</option>
<option value="IT" label="Italy">Italy</option>
</optgroup>
<optgroup id="country-optgroup-Africa" label="Africa">
<option value="DZ" label="Algeria">Algeria</option>
<option value="AO" label="Angola">Angola</option>
<option value="BJ" label="Benin">Benin</option>
<option value="BW" label="Botswana">Botswana</option>
<option value="BF" label="Burkina Faso">Burkina Faso</option>
<option value="BI" label="Burundi">Burundi</option>
<option value="CM" label="Cameroon">Cameroon</option>
<option value="CV" label="Cape Verde">Cape Verde</option>
<option value="CF" label="Central African Republic">Central African Republic</option>
<option value="TD" label="Chad">Chad</option>
<option value="KM" label="Comoros">Comoros</option>
<option value="CG" label="Congo - Brazzaville">Congo - Brazzaville</option>
<option value="CD" label="Congo - Kinshasa">Congo - Kinshasa</option>
<option value="CI" label="Côte d’Ivoire">Côte d’Ivoire</option>
<option value="DJ" label="Djibouti">Djibouti</option>
<option value="EG" label="Egypt">Egypt</option>
<option value="GQ" label="Equatorial Guinea">Equatorial Guinea</option>
<option value="ER" label="Eritrea">Eritrea</option>
<option value="ET" label="Ethiopia">Ethiopia</option>
<option value="GA" label="Gabon">Gabon</option>
<option value="GM" label="Gambia">Gambia</option>
<option value="GH" label="Ghana">Ghana</option>
<option value="GN" label="Guinea">Guinea</option>
<option value="GW" label="Guinea-Bissau">Guinea-Bissau</option>
<option value="KE" label="Kenya">Kenya</option>
<option value="LS" label="Lesotho">Lesotho</option>
<option value="LR" label="Liberia">Liberia</option>
<option value="LY" label="Libya">Libya</option>
<option value="MG" label="Madagascar">Madagascar</option>
<option value="MW" label="Malawi">Malawi</option>
<option value="ML" label="Mali">Mali</option>
<option value="MR" label="Mauritania">Mauritania</option>
<option value="MU" label="Mauritius">Mauritius</option>
<option value="YT" label="Mayotte">Mayotte</option>
<option value="MA" label="Morocco">Morocco</option>
<option value="MZ" label="Mozambique">Mozambique</option>
<option value="NA" label="Namibia">Namibia</option>
<option value="NE" label="Niger">Niger</option>
<option value="NG" label="Nigeria">Nigeria</option>
<option value="RW" label="Rwanda">Rwanda</option>
<option value="RE" label="Réunion">Réunion</option>
<option value="SH" label="Saint Helena">Saint Helena</option>
<option value="SN" label="Senegal">Senegal</option>
<option value="SC" label="Seychelles">Seychelles</option>
<option value="SL" label="Sierra Leone">Sierra Leone</option>
<option value="SO" label="Somalia">Somalia</option>
<option value="ZA" label="South Africa">South Africa</option>
<option value="SD" label="Sudan">Sudan</option>
<option value="SZ" label="Swaziland">Swaziland</option>
<option value="ST" label="São Tomé and Príncipe">São Tomé and Príncipe</option>
<option value="TZ" label="Tanzania">Tanzania</option>
<option value="TG" label="Togo">Togo</option>
<option value="TN" label="Tunisia">Tunisia</option>
<option value="UG" label="Uganda">Uganda</option>
<option value="EH" label="Western Sahara">Western Sahara</option>
<option value="ZM" label="Zambia">Zambia</option>
<option value="ZW" label="Zimbabwe">Zimbabwe</option>
</optgroup>
<optgroup id="country-optgroup-Americas" label="Americas">
<option value="AI" label="Anguilla">Anguilla</option>
<option value="AG" label="Antigua and Barbuda">Antigua and Barbuda</option>
<option value="AR" label="Argentina">Argentina</option>
<option value="AW" label="Aruba">Aruba</option>
<option value="BS" label="Bahamas">Bahamas</option>
<option value="BB" label="Barbados">Barbados</option>
<option value="BZ" label="Belize">Belize</option>
<option value="BM" label="Bermuda">Bermuda</option>
<option value="BO" label="Bolivia">Bolivia</option>
<option value="BR" label="Brazil">Brazil</option>
<option value="VG" label="British Virgin Islands">British Virgin Islands</option>
<option value="CA" label="Canada">Canada</option>
<option value="KY" label="Cayman Islands">Cayman Islands</option>
<option value="CL" label="Chile">Chile</option>
<option value="CO" label="Colombia">Colombia</option>
<option value="CR" label="Costa Rica">Costa Rica</option>
<option value="CU" label="Cuba">Cuba</option>
<option value="DM" label="Dominica">Dominica</option>
<option value="DO" label="Dominican Republic">Dominican Republic</option>
<option value="EC" label="Ecuador">Ecuador</option>
<option value="SV" label="El Salvador">El Salvador</option>
<option value="FK" label="Falkland Islands">Falkland Islands</option>
<option value="GF" label="French Guiana">French Guiana</option>
<option value="GL" label="Greenland">Greenland</option>
<option value="GD" label="Grenada">Grenada</option>
<option value="GP" label="Guadeloupe">Guadeloupe</option>
<option value="GT" label="Guatemala">Guatemala</option>
<option value="GY" label="Guyana">Guyana</option>
<option value="HT" label="Haiti">Haiti</option>
<option value="HN" label="Honduras">Honduras</option>
<option value="JM" label="Jamaica">Jamaica</option>
<option value="MQ" label="Martinique">Martinique</option>
<option value="MX" label="Mexico">Mexico</option>
<option value="MS" label="Montserrat">Montserrat</option>
<option value="AN" label="Netherlands Antilles">Netherlands Antilles</option>
<option value="NI" label="Nicaragua">Nicaragua</option>
<option value="PA" label="Panama">Panama</option>
<option value="PY" label="Paraguay">Paraguay</option>
<option value="PE" label="Peru">Peru</option>
<option value="PR" label="Puerto Rico">Puerto Rico</option>
<option value="BL" label="Saint Barthélemy">Saint Barthélemy</option>
<option value="KN" label="Saint Kitts and Nevis">Saint Kitts and Nevis</option>
<option value="LC" label="Saint Lucia">Saint Lucia</option>
<option value="MF" label="Saint Martin">Saint Martin</option>
<option value="PM" label="Saint Pierre and Miquelon">Saint Pierre and Miquelon</option>
<option value="VC" label="Saint Vincent and the Grenadines">Saint Vincent and the Grenadines</option>
<option value="SR" label="Suriname">Suriname</option>
<option value="TT" label="Trinidad and Tobago">Trinidad and Tobago</option>
<option value="TC" label="Turks and Caicos Islands">Turks and Caicos Islands</option>
<option value="VI" label="U.S. Virgin Islands">U.S. Virgin Islands</option>
<option value="US" label="United States">United States</option>
<option value="UY" label="Uruguay">Uruguay</option>
<option value="VE" label="Venezuela">Venezuela</option>
</optgroup>
<optgroup id="country-optgroup-Asia" label="Asia">
<option value="AF" label="Afghanistan">Afghanistan</option>
<option value="AM" label="Armenia">Armenia</option>
<option value="AZ" label="Azerbaijan">Azerbaijan</option>
<option value="BH" label="Bahrain">Bahrain</option>
<option value="BD" label="Bangladesh">Bangladesh</option>
<option value="BT" label="Bhutan">Bhutan</option>
<option value="BN" label="Brunei">Brunei</option>
<option value="KH" label="Cambodia">Cambodia</option>
<option value="CN" label="China">China</option>
<option value="GE" label="Georgia">Georgia</option>
<option value="HK" label="Hong Kong SAR China">Hong Kong SAR China</option>
<option value="IN" label="India">India</option>
<option value="ID" label="Indonesia">Indonesia</option>
<option value="IR" label="Iran">Iran</option>
<option value="IQ" label="Iraq">Iraq</option>
<option value="IL" label="Israel">Israel</option>
<option value="JP" label="Japan">Japan</option>
<option value="JO" label="Jordan">Jordan</option>
<option value="KZ" label="Kazakhstan">Kazakhstan</option>
<option value="KW" label="Kuwait">Kuwait</option>
<option value="KG" label="Kyrgyzstan">Kyrgyzstan</option>
<option value="LA" label="Laos">Laos</option>
<option value="LB" label="Lebanon">Lebanon</option>
<option value="MO" label="Macau SAR China">Macau SAR China</option>
<option value="MY" label="Malaysia">Malaysia</option>
<option value="MV" label="Maldives">Maldives</option>
<option value="MN" label="Mongolia">Mongolia</option>
<option value="MM" label="Myanmar [Burma]">Myanmar [Burma]</option>
<option value="NP" label="Nepal">Nepal</option>
<option value="NT" label="Neutral Zone">Neutral Zone</option>
<option value="KP" label="North Korea">North Korea</option>
<option value="OM" label="Oman">Oman</option>
<option value="PK" label="Pakistan">Pakistan</option>
<option value="PS" label="Palestinian Territories">Palestinian Territories</option>
<option value="YD" label="People's Democratic Republic of Yemen">People's Democratic Republic of Yemen</option>
<option value="PH" label="Philippines">Philippines</option>
<option value="QA" label="Qatar">Qatar</option>
<option value="SA" label="Saudi Arabia">Saudi Arabia</option>
<option value="SG" label="Singapore">Singapore</option>
<option value="KR" label="South Korea">South Korea</option>
<option value="LK" label="Sri Lanka">Sri Lanka</option>
<option value="SY" label="Syria">Syria</option>
<option value="TW" label="Taiwan">Taiwan</option>
<option value="TJ" label="Tajikistan">Tajikistan</option>
<option value="TH" label="Thailand">Thailand</option>
<option value="TL" label="Timor-Leste">Timor-Leste</option>
<option value="TR" label="Turkey">Turkey</option>
<option value="TM" label="Turkmenistan">Turkmenistan</option>
<option value="AE" label="United Arab Emirates">United Arab Emirates</option>
<option value="UZ" label="Uzbekistan">Uzbekistan</option>
<option value="VN" label="Vietnam">Vietnam</option>
<option value="YE" label="Yemen">Yemen</option>
</optgroup>
<optgroup id="country-optgroup-Europe" label="Europe">
<option value="AL" label="Albania">Albania</option>
<option value="AD" label="Andorra">Andorra</option>
<option value="AT" label="Austria">Austria</option>
<option value="BY" label="Belarus">Belarus</option>
<option value="BE" label="Belgium">Belgium</option>
<option value="BA" label="Bosnia and Herzegovina">Bosnia and Herzegovina</option>
<option value="BG" label="Bulgaria">Bulgaria</option>
<option value="HR" label="Croatia">Croatia</option>
<option value="CY" label="Cyprus">Cyprus</option>
<option value="CZ" label="Czech Republic">Czech Republic</option>
<option value="DK" label="Denmark">Denmark</option>
<!-- <option value="DD" label="East Germany">East Germany</option> -->
<option value="EE" label="Estonia">Estonia</option>
<option value="FO" label="Faroe Islands">Faroe Islands</option>
<option value="FI" label="Finland">Finland</option>
<option value="FR" label="France">France</option>
<option value="DE" label="Germany">Germany</option>
<option value="GI" label="Gibraltar">Gibraltar</option>
<option value="GR" label="Greece">Greece</option>
<option value="GG" label="Guernsey">Guernsey</option>
<option value="HU" label="Hungary">Hungary</option>
<option value="IS" label="Iceland">Iceland</option>
<option value="IE" label="Ireland">Ireland</option>
<option value="IM" label="Isle of Man">Isle of Man</option>
<option value="IT" label="Italy">Italy</option>
<option value="JE" label="Jersey">Jersey</option>
<option value="LV" label="Latvia">Latvia</option>
<option value="LI" label="Liechtenstein">Liechtenstein</option>
<option value="LT" label="Lithuania">Lithuania</option>
<option value="LU" label="Luxembourg">Luxembourg</option>
<option value="MK" label="Macedonia">Macedonia</option>
<option value="MT" label="Malta">Malta</option>
<option value="FX" label="Metropolitan France">Metropolitan France</option>
<option value="MD" label="Moldova">Moldova</option>
<option value="MC" label="Monaco">Monaco</option>
<option value="ME" label="Montenegro">Montenegro</option>
<option value="NL" label="Netherlands">Netherlands</option>
<option value="NO" label="Norway">Norway</option>
<option value="PL" label="Poland">Poland</option>
<option value="PT" label="Portugal">Portugal</option>
<option value="RO" label="Romania">Romania</option>
<option value="RU" label="Russia">Russia</option>
<option value="SM" label="San Marino">San Marino</option>
<option value="RS" label="Serbia">Serbia</option>
<option value="CS" label="Serbia and Montenegro">Serbia and Montenegro</option>
<option value="SK" label="Slovakia">Slovakia</option>
<option value="SI" label="Slovenia">Slovenia</option>
<option value="ES" label="Spain">Spain</option>
<option value="SJ" label="Svalbard and Jan Mayen">Svalbard and Jan Mayen</option>
<option value="SE" label="Sweden">Sweden</option>
<option value="CH" label="Switzerland">Switzerland</option>
<option value="UA" label="Ukraine">Ukraine</option>
<!-- <option value="SU" label="Union of Soviet Socialist Republics">Union of Soviet Socialist Republics</option> -->
<option value="GB" label="United Kingdom">United Kingdom</option>
<option value="VA" label="Vatican City">Vatican City</option>
<option value="AX" label="Åland Islands">Åland Islands</option>
</optgroup>
<optgroup id="country-optgroup-Oceania" label="Oceania">
<option value="AS" label="American Samoa">American Samoa</option>
<option value="AQ" label="Antarctica">Antarctica</option>
<option value="AU" label="Australia">Australia</option>
<option value="BV" label="Bouvet Island">Bouvet Island</option>
<option value="IO" label="British Indian Ocean Territory">British Indian Ocean Territory</option>
<option value="CX" label="Christmas Island">Christmas Island</option>
<option value="CC" label="Cocos [Keeling] Islands">Cocos [Keeling] Islands</option>
<option value="CK" label="Cook Islands">Cook Islands</option>
<option value="FJ" label="Fiji">Fiji</option>
<option value="PF" label="French Polynesia">French Polynesia</option>
<option value="TF" label="French Southern Territories">French Southern Territories</option>
<option value="GU" label="Guam">Guam</option>
<option value="HM" label="Heard Island and McDonald Islands">Heard Island and McDonald Islands</option>
<option value="KI" label="Kiribati">Kiribati</option>
<option value="MH" label="Marshall Islands">Marshall Islands</option>
<option value="FM" label="Micronesia">Micronesia</option>
<option value="NR" label="Nauru">Nauru</option>
<option value="NC" label="New Caledonia">New Caledonia</option>
<option value="NZ" label="New Zealand">New Zealand</option>
<option value="NU" label="Niue">Niue</option>
<option value="NF" label="Norfolk Island">Norfolk Island</option>
<option value="MP" label="Northern Mariana Islands">Northern Mariana Islands</option>
<option value="PW" label="Palau">Palau</option>
<option value="PG" label="Papua New Guinea">Papua New Guinea</option>
<option value="PN" label="Pitcairn Islands">Pitcairn Islands</option>
<option value="WS" label="Samoa">Samoa</option>
<option value="SB" label="Solomon Islands">Solomon Islands</option>
<option value="GS" label="South Georgia and the South Sandwich Islands">South Georgia and the South Sandwich Islands</option>
<option value="TK" label="Tokelau">Tokelau</option>
<option value="TO" label="Tonga">Tonga</option>
<option value="TV" label="Tuvalu">Tuvalu</option>
<option value="UM" label="U.S. Minor Outlying Islands">U.S. Minor Outlying Islands</option>
<option value="VU" label="Vanuatu">Vanuatu</option>
<option value="WF" label="Wallis and Futuna">Wallis and Futuna</option>
</optgroup>
</select>
"""


def too_soon():
    " you're early "
    print("""<!doctype html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8">
<meta name=viewport content="width=device-width, initial-scale=1">
<title>Secret Shipping 2024</title>
<style type="text/css">body{margin:2.5em auto;max-width:40em;line-height:1.5;font-size:18px;color:#444;padding:0 0.5em}h1,h2,h3{line-height:1.2}</style>
<style>body{font-family:sans-serif;}#seen{font-style:italic;text-align:center}</style>
""")
    print(f"""<body>
<div name=header>
<h1><span style="color:#f00">&#x2665;</span> Secret Shipping 2024 <span style="color:#f99">&#x2666;</span> <span style="color:#999">&#x2663;</span> <span style="color:#000">&#x2660;</span></h1>
<p><img src=shime33_100px.png style="float:right">
:33 &lt; You're here pawfully early; signups open at {OPEN_TIME} UTC.</p>
</div></body>""")


def too_late():
    " you're late "
    print("""<!doctype html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8">
<meta name=viewport content="width=device-width, initial-scale=1">
<title>Secret Shipping 2024</title>
<style type="text/css">body{margin:2.5em auto;max-width:40em;line-height:1.5;font-size:18px;color:#444;padding:0 0.5em}h1,h2,h3{line-height:1.2}</style>
<style>body{font-family:sans-serif;}#seen{font-style:italic;text-align:center}</style>
""")
    print(f"""<body>
<div name=header>
<h1><span style="color:#f00">&#x2665;</span> Secret Shipping 2024 <span style="color:#f99">&#x2666;</span> <span style="color:#999">&#x2663;</span> <span style="color:#000">&#x2660;</span></h1>
<p><img src=shime33_100px.png style="float:right">
:33 &lt; You're here pawfully late; signups ended at {CLOSED_TIME} UTC.</p>
</div></body>""")


def get_():
    " you didnt do nothin "
    print("""<!doctype html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8">
<meta name=viewport content="width=device-width, initial-scale=1">
<title>Secret Shipping 2024</title>
<style type="text/css">body{margin:2.5em auto;max-width:40em;line-height:1.5;font-size:18px;color:#444;padding:0 0.5em}h1,h2,h3{line-height:1.2}</style>
<style>body{font-family:sans-serif;}#seen{font-style:italic;text-align:center}</style>
<script>
var gebi = document.getElementById.bind(document)
function init(){
  fetch(window.location + "?seen")
  .then((res)=>res.text())
  .then((res)=>{{ gebi("seen").innerHTML = res; }})
}
window.addEventListener("load", init);
</script>
<meta name="twitter:title" content="Secret Shipping Signup 2024" />
<meta name="twitter:image" content="https://nepeta.mozai.com/secretshipping/checkem_y_cptnameless.100px.png" />
<meta name="twitter:card" content="Sign up for a Valentine's Day gift exchange" />
</head>""")
    print(f"""
<body>
<div name=header>
<h1><span style="color:#f00">&#x2665;</span> Secret Shipping 2024 <span style="color:#f99">&#x2666;</span> <span style="color:#999">&#x2663;</span> <span style="color:#000">&#x2660;</span></h1>
<p><img src=shime33_100px.png style="float:right">
Our olive shipping expert can s33 who's your match for the upcoming
February Human Quadrants Day.  Sign up to find out who could be your
special someone, and send them a gift so they know how Flushed/Pale/Pitch
you really feel about them</p>
<p>Sign-ups will be open between Jan 1st up to Jan 8th.  You'll get a
message telling you with whom you've been matched and a suggested quadrant.
We'll expect you to send them a modest gift(*) and a message in
the mail before Feb 14th.</p>
<p style=font-size:80%>(*: gift guide: * spend no more than a take-out
lunch in your part of the world. * For a flushed match, nothing pervy. *
For a pitched match, nothing mean. * hearts diamonds or spades, be
happy sending it and send something they'll be happy to recieve.) <!--<span
style=font-size:80%>(**: no ashen/clubs shipping, too complicated and
being an auspistice sounds like work.)</span>--></p>
</div>

<div><form id=form method=post><ol>
<li>What name would we know you by?<br><input size=20 id=Name name=Name maxlength=63 required></li>
<li>What email address should I use to send you results?<br><input size=30 id=Email name=Email required pattern="^[a-zA-Z].*@[a-zA-Z][0-9_a-zA-Z-].*" maxlength=128></li>
<li>When someone mails you a package, what name and address should they write?<br><textarea id=Address name=Address cols=40 rows=4 maxlength=4096 required></textarea></li>
<li>What should your special someone know about you before looking for your gift?<br><textarea id=Intro name=Intro cols=40 rows=4 maxlength=4096 required></textarea></li>
<li>To save me some typing, what country are you in?<br>{COUNTRIES_DROPDOWN}
</li>
<li>Are you cool with sending packages to a destination outside your country?<br><input type=radio name=ForeignOkay value=Y checked>Yes</input>&nbsp;<input type=radio name=ForeignOkay value=N>No</input></li>
<li>If/When your dreamself wakes up, which moon do you expect to find yourself upon?<br><input type=radio name=Moon value=Derse>Derse <input type=radio name=Moon value=Prospit>Prospit <input type=radio name=Moon value=Luna>Luna <input type=radio name=Moon value=DocScratch>Doc&nbsp;Scratch's&nbsp;apartment<input type=radio name=Moon value=Unknown checked>I&nbsp;don't&nbsp;know</li>
</ol><input type=submit name=Submit value="Sign Up"> <span id=seen></span></form>

<p id=promise style="font-style:italic;font-size:80%">
(By submitting your info, you are volunteering to send something
nice in the mail to a stranger.  I solemnly swear I will not give the
information you submit to anybody, with the exception of one participant
who volunteered to send you a gift.)</p>
</div>

</body>
""")


def get_seen():
    " have I seen you before? "
    remote_addr = os.environ.get("REMOTE_ADDR")
    cur = DBCONN.cursor()
    cur.execute("SELECT sum(1) FROM signups WHERE remote_addr = ?",
                [remote_addr])
    # cur.execute("SELECT sum(1) FROM signups WHERE remote_addr = :rm", {"rm": remote_addr})
    howmany = cur.fetchone()[0] or 0
    if howmany == 0:
        print("(This looks like your first visit)")
    elif howmany == 1:
        print("(Looks like you already signed up; you can do it again if you have multiple people in your home, or you want to fix a mistake.)")
    elif howmany > 31:
        print(
            f"(Looks like you signed up {howmany} times; if you're having trouble, talk to Mozai first.)")
    else:
        print(f"(Looks like you signed up {howmany} times)")


def _cook_formdata():
    " just give me a dict from either kind of POST request please "
    formdata = {}
    content_type = os.environ.get("CONTENT_TYPE")
    if content_type == "application/x-www-form-urlencoded":
        formdata = urllib.parse.parse_qs(sys.stdin.read())
    elif content_type == "multipart/form-data":
        payload = email.parser.BytesFeedParser(policy=email.policy.HTTP)
        payload.feed(f"Content-Type: {content_type}\r\n".encode('utf-8'))
        payload.feed('\r\n'.encode('utf-8'))
        for line in sys.stdin:
            payload.feed(line)
        mesg = payload.close()
        del payload
        assert mesg.is_multipart()
        for part in mesg.iter_parts():
            part.set_default_type(None)
            i = part.get_param('name', header='content-disposition')
            j = part.get_payload(decode=True)
            formdata[i] = j
            #print(f"""{part.get_param('name', header='content-disposition')}""")
            # print(f"""{part.get_filename(None)}""")
            # print(f"""{part.get_content_type()}""")
            # print(f"""{part.get_payload(decode=True)}""")
    return formdata


def _clean(instring):
    " percent-encode characters that look bad in sqlite3 output "
    instring = instring.replace("\r\n", '\n')
    i = []
    for j in instring:
        if j == '%':
            i.append("%%")
        elif j.isprintable():
            i.append(j)
        else:
            i.append(f"%{ord(j):02X}")
    return ''.join(i)


def post_():
    " POST request "
    print("""<!doctype html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8">
<meta name=viewport content="width=device-width, initial-scale=1">
<title>Secret Shipping 2024</title>
<style type="text/css">body{margin:2.5em auto;max-width:40em;line-height:1.5;font-size:18px;color:#444;padding:0 0.5em}h1,h2,h3{line-height:1.2}</style>
<style>body{font-family:sans-serif;}</style>
</head>""")
    cur = DBCONN.cursor()
    remote_addr = os.environ.get("REMOTE_ADDR")
    cur = DBCONN.cursor()
    cur.execute("SELECT sum(1) FROM signups WHERE remote_addr = ?",
                [remote_addr])
    howmany = cur.fetchone()[0] or 0
    if howmany > 31:
        print(f"""<body>
<div name=header>
<h1><span style="color:#f00">&#x2665;</span> Secret Shipping 2024 <span style="color:#f99">&#x2666;</span> <span style="color:#999">&#x2663;</span> <span style="color:#000">&#x2660;</span></h1>
<p><img src=equius_200px.png style="float:right">
D --&gt; You have already submitted {howmany} times<br>
D --&gt; I STRONGly suggest you ask for help before you make another attempt
</p></div></body>""")
        return
    cur.close()
    cur = DBCONN.cursor()
    formdata = _cook_formdata()
    nick = formdata.get("Name")[0][:63]
    params = (remote_addr,
              _clean(nick),
              _clean(formdata.get("Email")[0]),
              _clean(formdata.get("Address")[0]),
              _clean(formdata.get("Country")[0]),
              _clean(formdata.get("Intro")[0]),
              _clean(formdata.get("ForeignOkay")[0]),
              _clean(formdata.get("Moon")[0]))
    cur.execute("""INSERT INTO signups
      (tstamp, remote_addr, name, email, address, country, intro, foreignokay, moon)
      VALUES (datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?);""", params)
    DBCONN.commit()
    cur.close()
    nick = nick.replace('&', '&amp;').replace('<', '&lt;')
    if len(nick) > 40:
        nick = nick[:37] + "..."
    print(f"""<body>
<div name=header>
<h1><span style="color:#f00">&#x2665;</span> Secret Shipping 2024 <span style="color:#f99">&#x2666;</span> <span style="color:#999">&#x2663;</span> <span style="color:#000">&#x2660;</span></h1>
<p><img src=shime33_100px.png style="float:right">
:33 &lt; *ac salutes*  message received, {nick}!  You will hear from us purromptly.</p>
</div></body>""")


def initdb():
    " create the table in the database please "
    cur = DBCONN.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS signups
      (tstamp DATETIME, remote_addr, name, email, address, country,
      intro, foreignokay, moon);""")
    cur.close()


def pprint_dict(obj):
    " pprint a dict so its not all one line "
    for k in sorted(obj.keys()):
        print(f"  {k}: {obj[k]}")


def main():
    " Zhu Li!  do the thing! "
    req_method = os.environ.get("REQUEST_METHOD").upper()
    print("Content-Type: text/html\n")
    now = time.strftime("%Y-%m-%d %H:%M")
    if now < OPEN_TIME:
        too_soon()
    elif now > CLOSED_TIME:
        too_late()
    elif req_method == "POST":
        post_()
    else:
        query_string = os.environ.get("QUERY_STRING", "")
        # query_dict = urllib.parse.parse_qs(os.environ.get("QUERY_STRING", ""))
        if query_string == "seen":
            get_seen()
        else:
            get_()


DBCONN = sqlite3.connect("ss2024.db")
DBCONN.row_factory = sqlite3.Row
main()
DBCONN.commit()
DBCONN.close()
