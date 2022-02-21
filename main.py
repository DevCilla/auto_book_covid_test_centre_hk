from playwright.sync_api import sync_playwright
import datetime
from datetime import datetime, timedelta
import random


async def capScreen(page_elm):
    await page_elm.screenshot(path="booking.ng", full_page=True)


def chok(page_elm, date_elm, desired_district, desired_centre):
    other_dist = random.sample(range(1, 18), 17)
    if int(desired_district) in other_dist:
        other_dist.remove(int(desired_district))
    while page_elm.locator('label[class=\"timeslots_label_\"]').nth(0).inner_text().find(date_elm.strftime('%Y-%m-%d')) == -1:
        rand_dist = str(random.choice(other_dist))
        page_elm.locator("select[name=\"step_2_district\"]").select_option(rand_dist)
        page_elm.locator("select[name=\"step_2_district\"]").select_option(desired_district)
        page_elm.locator("select[name=\"step_2_center\"]").select_option(desired_centre)
        if page_elm.locator('label[class=\"timeslots_label_\"]').nth(0).inner_text().find(date_elm.strftime('%Y-%m-%d')) == 1:
            #print("Has booking:" + str(page_elm.locator('label[class=\"timeslots_label_\"]').nth(0).inner_text()))
            break

    time_slot_list = page_elm.locator("input[type=\"radio\"][name=\"step_2_booking_timeslot\"][value]")
    i = 0
    while i <= time_slot_list.count():
        #print("i = " + str(i))
        if time_slot_list.nth(i).is_enabled():
            time_slot_list.nth(i).click()
            break
        i += 1

    page_elm.locator("text=下一步").click()
    page_elm.locator("input:has-text(\"確認\")").click()

    if page_elm.is_visible("li:has-text(\"你選擇的時段預約已滿。\")"):
        return False
    elif page_elm.is_visible("button#btnScreenShot"):
        return True


def run(playwright_elm):
    # input value setting
    today_a = datetime.today()
    tomorrow = today_a + timedelta(days=1)
    hkid_prefix = 'hkid'
    hkid_check_digit = 'hkid_check_digit'
    surname = 'chin or eng surname'
    given_name = 'chin or eng given name'
    # select language
    #lang_pref = '#step_2_language_preference_english'
    lang_pref = '#step_2_language_preference_chinese'
    sms_phone = 'your sms number'
    desired_district = "4"  # pick from the list at the bottom of this file
    desired_centre = "6"  # pick from the list at the bottom of this file

    # programme start
    browser = playwright_elm.chromium.launch(headless=False)
    context = browser.new_context()

    page = context.new_page()
    context.tracing.start(screenshots=True, snapshots=True)
    page.goto('https://booking.communitytest.gov.hk/form/index_tc.jsp')
    page.wait_for_load_state()

    page.fill('#step_1_documentId_HKIC_prefix', hkid_prefix)
    page.fill('#step_1_documentId_HKIC_check_digit', hkid_check_digit)
    page.click('input[data-role="BOOKING"]')

    page.wait_for_selector('span.ckbox-checkmark') # if reCAPTCHA appears and needs human input
    page.locator('span.ckbox-checkmark').click()
    page.locator("text=下一頁").click()
    page.wait_for_load_state()
    page.click(lang_pref)
    page.locator("input#step_2_surname").scroll_into_view_if_needed(timeout=1000)
    page.fill('#step_2_surname', surname)
    page.fill('#step_2_givenname', given_name)
    page.fill('#step_2_tel_for_sms_notif', sms_phone)
    page.fill('#step_2_tel_for_sms_notif_confirm', sms_phone)

    # District
    page.locator("select[name=\"step_2_district\"]").scroll_into_view_if_needed(timeout=1000)
    page.locator("select[name=\"step_2_district\"]").select_option(desired_district)  # select District
    # Centre
    page.locator("select[name=\"step_2_center\"]").select_option(desired_centre)  # select Centre

    while chok(page, today_a, desired_district, desired_centre):
        page.evaluate("console.log('" + today_a.strftime('%Y-%m-%d %H:%M:%S') + "')")
        capScreen(page)
        break

    page.locator("button#btnScreenShot").scroll_into_view_if_needed(timeout=1000)
    page.locator("button#btnScreenShot").click()
    now = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    context.tracing.stop(path="trace_" + now + ".zip")
    page.pause()


with sync_playwright() as playwright:
    run(playwright).setTimeout(9999999)

# value of district and centre
# <select id="step_2_district" name="step_2_district" class="form-control" onchange="" required="">
# <option disabled="" selected="" hidden="" value="">請選擇地區</option>
# <option value="1">離島區</option>
# <option value="2">葵青區</option>
# <option value="3">北區</option>
# <option value="4">西貢區</option>
# <option value="5">沙田區</option>
# <option value="6">大埔區</option>
# <option value="7">荃灣區</option>
# <option value="8">屯門區</option>
# <option value="9">元朗區</option>
# <option value="10">九龍城區</option>
# <option value="11">觀塘區</option>
# <option value="12">深水埗區</option>
# <option value="13">黃大仙區</option>
# <option value="14">油尖旺區</option>
# <option value="15">中西區</option>
# <option value="16">東區</option>
# <option value="17">南區</option>
# <option value="18">灣仔區</option>
# </select>
#
# <select id="step_2_center" name="step_2_center" class="form-control" onchange="" required="">
# <option disabled="" selected="" hidden="" value="">請選擇測試中心</option>
# <option value="1" ctc_eng_name="Quarry Bay Community Hall" ctc_tc_name="鰂魚涌社區會堂" ctc_sc_name="鲗鱼涌社区会堂">鰂魚涌社區會堂</option>
# <option value="2" ctc_eng_name="Henry G. Leong Yau Ma Tei Community Centre" ctc_tc_name="梁顯利油麻地社區中心" ctc_sc_name="梁显利油麻地社区中心">梁顯利油麻地社區中心</option>
# <option value="3" ctc_eng_name="Lek Yuen Community Hall" ctc_tc_name="瀝源社區會堂" ctc_sc_name="沥源社区会堂">瀝源社區會堂</option>
# <option value="4" ctc_eng_name="Yuen Long Town East Community Hall" ctc_tc_name="元朗市東社區會堂" ctc_sc_name="元朗市东社区会堂">元朗市東社區會堂</option>
# <option value="5" ctc_eng_name="Yau Tong Community Hall" ctc_tc_name="油塘社區會堂" ctc_sc_name="油塘社区会堂">油塘社區會堂</option></select>
# <option value="6" ctc_eng_name="Hang Hau Community Hall" ctc_tc_name="坑口社區會堂" ctc_sc_name="坑口社区会堂">坑口社區會堂</option>
# <option value="7" ctc_eng_name="Wo Hing Community Hall" ctc_tc_name="和興社區會堂" ctc_sc_name="和兴社区会堂">和興社區會堂</option>
# <option value="8" ctc_eng_name="Siu Lun Community Hall" ctc_tc_name="兆麟社區會堂" ctc_sc_name="兆麟社区会堂">兆麟社區會堂</option>
# <option value="9" ctc_eng_name="Lai King Community Hall" ctc_tc_name="荔景社區會堂" ctc_sc_name="荔景社区会堂">荔景社區會堂</option>
# <option value="10" ctc_eng_name="Leighton Hill Community Hall" ctc_tc_name="禮頓山社區會堂" ctc_sc_name="礼顿山社区会堂">禮頓山社區會堂</option>
# <option value="11" ctc_eng_name="Pak Tin Community Hall (G/F Pak Tin Community Complex at Pak Wan Street)" ctc_tc_name="白田社區會堂 (白雲街白田社區綜合大樓地下)" ctc_sc_name="白田社区会堂 (白云街白田社区综合大楼地下)">白田社區會堂 (白雲街白田社區綜合大樓地下)</option>
# <option value="13" ctc_eng_name="Wai Tsuen Sports Centre" ctc_tc_name="蕙荃體育館" ctc_sc_name="蕙荃体育馆">蕙荃體育館</option>
# <option value="14" ctc_eng_name="Tai Wo Sports Centre" ctc_tc_name="太和體育館" ctc_sc_name="太和体育馆">太和體育館</option>
# <option value="15" ctc_eng_name="Shek Tong Tsui Sports Centre" ctc_tc_name="石塘咀體育館" ctc_sc_name="石塘咀体育馆">石塘咀體育館</option>
# <option value="16" ctc_eng_name="To Kwa Wan Sports Centre" ctc_tc_name="土瓜灣體育館" ctc_sc_name="土瓜湾体育馆">土瓜灣體育館</option>
# <option value="17" ctc_eng_name="Ngau Tau Kok Road Sports Centre" ctc_tc_name="牛頭角道體育館" ctc_sc_name="牛头角道体育馆">牛頭角道體育館</option>
# <option value="20" ctc_eng_name="Lei Tung Community Hall" ctc_tc_name="利東社區會堂" ctc_sc_name="利东社区会堂">利東社區會堂</option>
# <option value="22" ctc_eng_name="Tung Tau Community Centre" ctc_tc_name="東頭社區中心" ctc_sc_name="东头社区中心">東頭社區中心</option>
# <option value="23" ctc_eng_name="Ground Transportation Lounge, Hong Kong International Airport" ctc_tc_name="香港國際機場地面運輸候車室" ctc_sc_name="香港国际机场地面运输候车室">香港國際機場地面運輸候車室</option>
# </select>
