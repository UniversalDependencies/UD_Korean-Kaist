#!/usr/bin/env python3
"""Fix too-many-subjects errors in UD_Korean-Kaist (dev branch).

Two error types addressed:
  nsubj+nsubj: classic double-subject construction → outer NP becomes nsubj:outer
  nsubj+csubj: copular/resultative 되다 construction → nsubj becomes nsubj:outer

Usage:
    python3 fix_ko_kaist_too_many_subjects.py

The script modifies the three CoNLL-U files in ~/UD_Korean-Kaist/ in place.
"""
import os
import udapi

FIXES = {
    # M2TA_064-s11 [train]
    # TEXT: 무엇보다도 문화에는 그 도덕성이 절대적인 기준이 되기 때문이다.
    # TRANSLIT: mu.eos.bo.da.do mun.hwa.e.neun geu do.deog.seong.i jeol.dae.jeog.in gi.jun.i doe.gi ddae.mun.i.da
    # ENGLISH: Above all, morality in culture is the absolute standard.
    # CONFLICT: N1:도덕성이(nsubj), N2:기준이(csubj) under pred:'되기 .doe.gi' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'M2TA_064-s11': [('deprel', 4, 'nsubj:outer')],

    # M2TA_065-s48 [train]
    # TEXT: 제 철에 난 것만이 대자연의 기를 듬뿍 지니고 있으며, 그것이 우리들의 피와 살이 되기 때문이다.
    # TRANSLIT: je cheol.e nan geos.man.i dae.ja.yeon.yi gi.reul deum.bbug ji.ni.go iss.eu.myeo , geu.geos.i u.ri.deul.yi pi.wa sal.i doe.gi ddae.mun.i.da
    # ENGLISH: Only what is harvested in season carries the full energy of great nature, becoming our very blood and flesh.
    # CONFLICT: N1:그것이(nsubj), N2:피와(csubj) under pred:'되기 .doe.gi' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'M2TA_065-s48': [('deprel', 11, 'nsubj:outer')],

    # M2TA_065-s83 [train]
    # TEXT: 만약 그것들이 맛이 없었다면 지금처럼 엄청나게 먹어대지는 않을 것이다.
    # TRANSLIT: man.yag geu.geos.deul.i mas.i eobs.eoss.da.myeon ji.geum.cheo.reom eom.cheong.na.ge meog.eo.dae.ji.neun anh.eul geos.i.da
    # ENGLISH: If those things had not been tasty, they would not be eaten as abundantly as they are now.
    # CONFLICT: N1:그것들이(nsubj), N2:맛이(nsubj) under pred:'없었다면 .eobs.eoss.da.myeon' → default: N1(그것들이)→nsubj:outer [NEEDS REVIEW]
    'M2TA_065-s83': [('deprel', 2, 'nsubj:outer')],

    # M2TA_069-s33 [dev]
    # TEXT: 정동이 한국의 신문화 신교육의 발상지가 된 내력을 말했으니, 이제는 서양식 신교육이 본격적으로 전래하던 시초를 말해야겠다.
    # TRANSLIT: jeong.dong.i han.gug.yi sin.mun.hwa sin.gyo.yug.yi bal.sang.ji.ga doen nae.ryeog.eul mal.haess.eu.ni , i.je.neun seo.yang.sig sin.gyo.yug.i bon.gyeog.jeog.eu.ro jeon.rae.ha.deon si.cho.reul mal.hae.ya.gess.da
    # ENGLISH: Having described how Jeongdong became the birthplace of Korea's new culture and new education, I must now speak of the first moment Western-style education arrived in earnest.
    # CONFLICT: N1:정동이(nsubj), N2:발상지가(csubj) under pred:'된 .doen' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'M2TA_069-s33': [('deprel', 1, 'nsubj:outer')],

    # M2TA_069-s49 [dev]
    # TEXT: 서울 선교사들은 밀의두가 앞으로 이상적 교장이 되리라고 기대했다.
    # TRANSLIT: seo.ul seon.gyo.sa.deul.eun mil.yi.du.ga ap.eu.ro i.sang.jeog gyo.jang.i doe.ri.ra.go gi.dae.haess.da
    # ENGLISH: The Seoul missionaries expected that Millidou would become an ideal principal.
    # CONFLICT: N1:밀의두가(nsubj), N2:교장이(csubj) under pred:'되리라고 .doe.ri.ra.go' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'M2TA_069-s49': [('deprel', 3, 'nsubj:outer')],

    # M2TA_072-s23 [train]
    # TEXT: 병 이름은 같아도 갑에게 효과 있는 약이 을에게는 효과가 없는 것은 이 개인차에 연유하는 것이다.
    # TRANSLIT: byeong i.reum.eun gat.a.do gab.e.ge hyo.gwa iss.neun yag.i eul.e.ge.neun hyo.gwa.ga eobs.neun geos.eun i gae.in.cha.e yeon.yu.ha.neun geos.i.da
    # ENGLISH: Even when the disease name is the same, the medicine effective for person A is ineffective for person B — this stems from individual differences.
    # CONFLICT: N1:약이(nsubj), N2:효과가(nsubj) under pred:'없는 .eobs.neun' → default: N1(약이)→nsubj:outer [NEEDS REVIEW]
    'M2TA_072-s23': [('deprel', 7, 'nsubj:outer')],

    # M2TA_073-s26 [train]
    # TEXT: 옆으로 기울어진 차량이 똑바로 있는 것보다 안정성이 높다.
    # TRANSLIT: yeop.eu.ro gi.ul.eo.jin cha.ryang.i ddog.ba.ro iss.neun geos.bo.da an.jeong.seong.i nop.da
    # ENGLISH: A car tilted sideways has higher stability than one standing upright.
    # CONFLICT: N1:차량이(nsubj), N2:안정성이(nsubj) under pred:'높다 .nop.da' → default: N1(차량이)→nsubj:outer [NEEDS REVIEW]
    'M2TA_073-s26': [('deprel', 3, 'nsubj:outer')],

    # M2TA_073-s28 [train]
    # TEXT: 자전거는 크게 기울어진 자세로 그 커브를 따라 달려가는데도 엎어지지 않을 뿐더러 이런 자세일 때가 가장 안정성이 있다.
    # TRANSLIT: ja.jeon.geo.neun keu.ge gi.ul.eo.jin ja.se.ro geu keo.beu.reul dda.ra dal.ryeo.ga.neun.de.do eop.eo.ji.ji anh.eul bbun.deo.reo i.reon ja.se.il ddae.ga ga.jang an.jeong.seong.i iss.da
    # ENGLISH: A bicycle neither falls when following a sharp curve in a greatly tilted posture, nor is it more stable than in any other posture.
    # CONFLICT: N1:때가(nsubj), N2:안정성이(nsubj) under pred:'있다 .iss.da' → default: N1(때가)→nsubj:outer [NEEDS REVIEW]
    'M2TA_073-s28': [('deprel', 14, 'nsubj:outer')],

    # M2TA_074-s3 [train]
    # TEXT: 정보 그 자체가 부와 권력의 근원이 되는 사회가 정보사회인 것이다.
    # TRANSLIT: jeong.bo geu ja.che.ga bu.wa gweon.ryeog.yi geun.weon.i doe.neun sa.hoe.ga jeong.bo.sa.hoe.in geos.i.da
    # ENGLISH: An information society is one in which information itself becomes the source of wealth and power.
    # CONFLICT: N1:자체가(nsubj), N2:근원이(csubj) under pred:'되는 .doe.neun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'M2TA_074-s3': [('deprel', 3, 'nsubj:outer')],

    # M2TA_082-s44 [train]
    # TEXT: 유한킴벌리는 한 그루의 나무가 숲이 되고, 우리 강산이 푸르러질 때까지 계속 나무를 심고 가꾸어 나갈 것입니다.
    # TRANSLIT: yu.han.kim.beol.ri.neun han geu.ru.yi na.mu.ga sup.i doe.go , u.ri gang.san.i pu.reu.reo.jil ddae.gga.ji gye.sog na.mu.reul sim.go ga.ggu.eo na.gal geos.ib.ni.da
    # ENGLISH: Yuhan-Kimberly will continue to plant and tend trees until one tree becomes a forest and our mountains and rivers turn green.
    # CONFLICT: N1:나무가(nsubj), N2:숲이(csubj) under pred:'되고 .doe.go' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'M2TA_082-s44': [('deprel', 4, 'nsubj:outer')],

    # M2TA_082-s63 [train]
    # TEXT: 제가 다니는 기계공학과에는 외국인 학생이 스무명이 넘어요.
    # TRANSLIT: je.ga da.ni.neun gi.gye.gong.hag.gwa.e.neun oe.gug.in hag.saeng.i seu.mu.myeong.i neom.eo.yo
    # ENGLISH: There are more than twenty foreign students in the mechanical engineering department where I study.
    # CONFLICT: N1:학생이(nsubj), N2:스무명이(nsubj) under pred:'넘어요 .neom.eo.yo' → default: N1(학생이)→nsubj:outer [NEEDS REVIEW]
    'M2TA_082-s63': [('deprel', 5, 'nsubj:outer')],

    # M2TA_083-s58 [train]
    # TEXT: 머리카락이 묻고 더러운 것이 남아 있으면, 마치 쓰레기를 쏟은 것 같아서 품위가 깎이게 된다.
    # TRANSLIT: meo.ri.ka.rag.i mud.go deo.reo.un geos.i nam.a iss.eu.myeon , ma.chi sseu.re.gi.reul ssod.eun geos gat.a.seo pum.wi.ga ggagg.i.ge doen.da
    # ENGLISH: If hair and dirt remain, it looks as if garbage has been spilled, which diminishes one's dignity.
    # CONFLICT: N1:머리카락이(nsubj), N2:것이(nsubj) under pred:'남아 .nam.a' → default: N1(머리카락이)→nsubj:outer [NEEDS REVIEW]
    'M2TA_083-s58': [('deprel', 1, 'nsubj:outer')],

    # M2TA_084-s184 [train]
    # TEXT: 모범이 최고의 교과서가 된다.
    # TRANSLIT: mo.beom.i choe.go.yi gyo.gwa.seo.ga doen.da
    # ENGLISH: A role model is the best textbook.
    # CONFLICT: N1:모범이(nsubj), N2:교과서가(csubj) under pred:'된다 .doen.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'M2TA_084-s184': [('deprel', 1, 'nsubj:outer')],

    # M2TA_084-s91 [train]
    # TEXT: 한 방울씩 떨어지는 물이 어느새 한 통이 된다.
    # TRANSLIT: han bang.ul.ssig ddeol.eo.ji.neun mul.i eo.neu.sae han tong.i doen.da
    # ENGLISH: Water falling drop by drop fills an entire bucket before you know it.
    # CONFLICT: N1:물이(nsubj), N2:통이(csubj) under pred:'된다 .doen.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'M2TA_084-s91': [('deprel', 4, 'nsubj:outer')],

    # M2TA_087-s140 [train]
    # TEXT: 그러다가 이 인형들이 작품이 될까 하는 의구심도 들었다.
    # TRANSLIT: geu.reo.da.ga i in.hyeong.deul.i jag.pum.i doel.gga ha.neun yi.gu.sim.do deul.eoss.da
    # ENGLISH: I wondered whether these dolls would ever become works of art.
    # CONFLICT: N1:인형들이(nsubj), N2:작품이(csubj) under pred:'될까 .doel.gga' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'M2TA_087-s140': [('deprel', 3, 'nsubj:outer')],

    # M2TA_087-s49 [train]
    # TEXT: 그 쪽이 마음이 편했다.
    # TRANSLIT: geu jjog.i ma.eum.i pyeon.haess.da
    # ENGLISH: That side felt more comfortable.
    # CONFLICT: N1:쪽이(nsubj), N2:마음이(nsubj) under pred:'편했다 .pyeon.haess.da' → default: N1(쪽이)→nsubj:outer [NEEDS REVIEW]
    'M2TA_087-s49': [('deprel', 2, 'nsubj:outer')],

    # M2TA_087-s77 [train]
    # TEXT: 혼자 평생을 외롭게 산다는 것이 정말 자신이 없었다.
    # TRANSLIT: hon.ja pyeong.saeng.eul oe.rob.ge san.da.neun geos.i jeong.mal ja.sin.i eobs.eoss.da
    # ENGLISH: I truly lacked the confidence to live alone for a lifetime.
    # CONFLICT: N1:것이(nsubj), N2:자신이(nsubj) under pred:'없었다 .eobs.eoss.da' → default: N1(것이)→nsubj:outer [NEEDS REVIEW]
    'M2TA_087-s77': [('deprel', 5, 'nsubj:outer')],

    # M2TA_088-s46 [train]
    # TEXT: 과연 돌돌 말은 종이가 붓 속에서 나왔다.
    # TRANSLIT: gwa.yeon dol.dol mal.eun jong.i.ga bus sog.e.seo na.wass.da
    # ENGLISH: Indeed, the rolled paper came out from inside the brush.
    # CONFLICT: N1:종이가(nsubj), N2:속에서(nsubj) under pred:'나왔다 .na.wass.da' → default: N1(종이가)→nsubj:outer [NEEDS REVIEW]
    'M2TA_088-s46': [('deprel', 4, 'nsubj:outer')],

    # M2TA_089-s1 [dev]
    # TEXT: 백화점에 가면 정말 내가 왕이 된 기분이었지요.
    # TRANSLIT: baeg.hwa.jeom.e ga.myeon jeong.mal nae.ga wang.i doen gi.bun.i.eoss.ji.yo
    # ENGLISH: Whenever I went to a department store, I truly felt as if I had become a king.
    # CONFLICT: N1:내가(nsubj), N2:왕이(csubj) under pred:'된 .doen' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'M2TA_089-s1': [('deprel', 4, 'nsubj:outer')],

    # M2TA_089-s23 [dev]
    # TEXT: 일본에만 오면 남편들이 사고가 나니까요.
    # TRANSLIT: il.bon.e.man o.myeon nam.pyeon.deul.i sa.go.ga na.ni.gga.yo
    # ENGLISH: Husbands tend to get into trouble whenever they come to Japan.
    # CONFLICT: N1:남편들이(nsubj), N2:사고가(nsubj) under pred:'나니까요 .na.ni.gga.yo' → default: N1(남편들이)→nsubj:outer [NEEDS REVIEW]
    'M2TA_089-s23': [('deprel', 3, 'nsubj:outer')],

    # M2TA_090-s45 [test]
    # TEXT: 이 단계에서 그 회사가 무엇이 잘못되고 무엇이 잘되고 있는가를 발견하게 된다.
    # TRANSLIT: i dan.gye.e.seo geu hoe.sa.ga mu.eos.i jal.mos.doe.go mu.eos.i jal.doe.go iss.neun.ga.reul bal.gyeon.ha.ge doen.da
    # ENGLISH: At this stage one discovers what the company is doing wrong and what it is doing right.
    # CONFLICT: N1:회사가(nsubj), N2:무엇이(nsubj) under pred:'잘못되고 .jal.mos.doe.go' → default: N1(회사가)→nsubj:outer [NEEDS REVIEW]
    'M2TA_090-s45': [('deprel', 4, 'nsubj:outer')],

    # M2TA_092-s69 [train]
    # TEXT: 지사이야쓰가를 연발하던 왜놈 형사는 눈을 치뜨고 노려보는 내가 기가 찼던지 도로 유치장에 가두었다.
    # TRANSLIT: ji.sa.i.ya.sseu.ga.reul yeon.bal.ha.deon wae.nom hyeong.sa.neun nun.eul chi.ddeu.go no.ryeo.bo.neun nae.ga gi.ga chass.deon.ji do.ro yu.chi.jang.e ga.du.eoss.da
    # ENGLISH: The Japanese detective who kept bowing could not believe how full of spirit I was and threw me back in the detention cell.
    # CONFLICT: N1:내가(nsubj), N2:기가(nsubj) under pred:'찼던지 .chass.deon.ji' → default: N1(내가)→nsubj:outer [NEEDS REVIEW]
    'M2TA_092-s69': [('deprel', 8, 'nsubj:outer')],

    # MH2_0010-s103 [test]
    # TEXT: 세종기지와 칠레기지 사이의 바다를 건넌다는 것이 그리 쉬운 일이 아니기 때문이다.
    # TRANSLIT: se.jong.gi.ji.wa chil.re.gi.ji sa.i.yi ba.da.reul geon.neon.da.neun geos.i geu.ri swi.un il.i a.ni.gi ddae.mun.i.da
    # ENGLISH: Crossing the sea between King Sejong Station and the Chilean station is no easy matter.
    # CONFLICT: N1:것이(nsubj), N2:일이(csubj) under pred:'아니기 .a.ni.gi' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0010-s103': [('deprel', 6, 'nsubj:outer')],

    # MH2_0010-s107 [test]
    # TEXT: 그러나 그에게는 문제가 시간이지 체류비용이 아닌 것이다.
    # TRANSLIT: geu.reo.na geu.e.ge.neun mun.je.ga si.gan.i.ji che.ryu.bi.yong.i a.nin geos.i.da
    # ENGLISH: For him, however, the problem was time, not the cost of staying.
    # CONFLICT: N1:문제가(nsubj), N2:체류비용이(csubj) under pred:'아닌 .a.nin' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0010-s107': [('deprel', 3, 'nsubj:outer')],

    # MH2_0010-s154 [test]
    # TEXT: 높이 약 20, 30 미터 또는 그 이상의 빙벽이 작게는 수미터, 크게는 수십미터가 무너져 내린다.
    # TRANSLIT: nop.i yag 20 , 30 mi.teo ddo.neun geu i.sang.yi bing.byeog.i jag.ge.neun su.mi.teo , keu.ge.neun su.sib.mi.teo.ga mu.neo.jyeo nae.rin.da
    # ENGLISH: Ice cliffs some 20 to 30 metres high — or even taller — collapse in falls ranging from a few metres to tens of metres.
    # CONFLICT: N1:빙벽이(nsubj), N2:수십미터가(nsubj) under pred:'무너져 .mu.neo.jyeo' → default: N1(빙벽이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0010-s154': [('deprel', 10, 'nsubj:outer')],

    # MH2_0010-s169 [test]
    # TEXT: 영롱한 공기방울의 형태도 신비하나 더 신비로운 것은 이 공기가 요즈음의 공기가 아니라는 데에 있다.
    # TRANSLIT: yeong.rong.han gong.gi.bang.ul.yi hyeong.tae.do sin.bi.ha.na deo sin.bi.ro.un geos.eun i gong.gi.ga yo.jeu.eum.yi gong.gi.ga a.ni.ra.neun de.e iss.da
    # ENGLISH: The shape of the shimmering air bubbles is mysterious in itself, but even more mysterious is the fact that this air is not modern air.
    # CONFLICT: N1:공기가(nsubj), N2:공기가(csubj) under pred:'아니라는 .a.ni.ra.neun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0010-s169': [('deprel', 9, 'nsubj:outer')],

    # MH2_0010-s246 [test]
    # TEXT: 2월의 폭풍설에도 기지주변이 하얗게 되고 장소에 따라서는 쌓인 눈이 1 미터 정도가 되었다.
    # TRANSLIT: 2.weol.yi pog.pung.seol.e.do gi.ji.ju.byeon.i ha.yah.ge doe.go jang.so.e dda.ra.seo.neun ssah.in nun.i 1 mi.teo jeong.do.ga doe.eoss.da
    # ENGLISH: Even in the February blizzard the area around the base turned white, and in some spots the accumulated snow reached about one metre.
    # CONFLICT: N1:눈이(nsubj), N2:정도가(csubj) under pred:'되었다 .doe.eoss.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0010-s246': [('deprel', 9, 'nsubj:outer')],

    # MH2_0010-s280 [test]
    # TEXT: 펭귄이 아직도 두 마리가 있었고 주위의 눈이 황갈색으로 더럽혀진 것을 보아 펭귄들이 집결했던 것이 분명하다.
    # TRANSLIT: peng.gwin.i a.jig.do du ma.ri.ga iss.eoss.go ju.wi.yi nun.i hwang.gal.saeg.eu.ro deo.reob.hyeo.jin geos.eul bo.a peng.gwin.deul.i jib.gyeol.haess.deon geos.i bun.myeong.ha.da
    # ENGLISH: Two penguins were still there, and the surrounding snow was stained yellowish-brown, making it clear that penguins had gathered there.
    # CONFLICT: N1:펭귄이(nsubj), N2:마리가(nsubj) under pred:'있었고 .iss.eoss.go' → default: N1(펭귄이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0010-s280': [('deprel', 1, 'nsubj:outer')],

    # MH2_0010-s30 [test]
    # TEXT: 160톤짜리 저유탱크가 6기가 있고 목조창고와 컨테이너, 부두와 펌프시설이 있다.
    # TRANSLIT: 160.ton.jja.ri jeo.yu.taeng.keu.ga 6.gi.ga iss.go mog.jo.chang.go.wa keon.te.i.neo , bu.du.wa peom.peu.si.seol.i iss.da
    # ENGLISH: There are six 160-tonne oil storage tanks, a wooden warehouse and containers, a pier, and pump facilities.
    # CONFLICT: N1:저유탱크가(nsubj), N2:6기가(nsubj) under pred:'있고 .iss.go' → default: N1(저유탱크가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0010-s30': [('deprel', 2, 'nsubj:outer')],

    # MH2_0010-s334 [test]
    # TEXT: 태양 질수록 햇빛의 영향은 작아져 시간이 많이 흐르면서 북서쪽 능선전체가 진한 붉은 색이 된다.
    # TRANSLIT: tae.yang jil.su.rog haes.bich.yi yeong.hyang.eun jag.a.jyeo si.gan.i manh.i heu.reu.myeon.seo bug.seo.jjog neung.seon.jeon.che.ga jin.han burg.eun saeg.i doen.da
    # ENGLISH: As the sun sets its effect diminishes, and over time the entire north-western ridge turns a deep red.
    # CONFLICT: N1:능선전체가(nsubj), N2:색이(csubj) under pred:'된다 .doen.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0010-s334': [('deprel', 10, 'nsubj:outer')],

    # MH2_0010-s347 [test]
    # TEXT: 그보다는 이날이 북반구에서 낮시간이 제일 길듯이 남반구에서 밤이 제일 길어 그만큼 생활하기 어려운 날이라고 할 수 있다.
    # TRANSLIT: geu.bo.da.neun i.nal.i bug.ban.gu.e.seo naj.si.gan.i je.il gil.deus.i nam.ban.gu.e.seo bam.i je.il gil.eo geu.man.keum saeng.hwal.ha.gi eo.ryeo.un nal.i.ra.go hal su iss.da
    # ENGLISH: Rather, just as this day has the longest daylight hours in the northern hemisphere, the southern hemisphere has the longest night, making it a particularly difficult day to live through.
    # CONFLICT: N1:이날이(nsubj), N2:낮시간이(nsubj) under pred:'길듯이 .gil.deus.i' → default: N1(이날이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0010-s347': [('deprel', 2, 'nsubj:outer')],

    # MH2_0010-s54 [test]
    # TEXT: 게다가 열풍난방방식이 문제가 생겨 운행자체도 문제고, 기계가 낡아지면서 열풍이 나오기 시작하면 짧은 순간이나 심한 기름냄새가 풍겼다.
    # TRANSLIT: ge.da.ga yeol.pung.nan.bang.bang.sig.i mun.je.ga saeng.gyeo un.haeng.ja.che.do mun.je.go , gi.gye.ga narg.a.ji.myeon.seo yeol.pung.i na.o.gi si.jag.ha.myeon jjarb.eun sun.gan.i.na sim.han gi.reum.naem.sae.ga pung.gyeoss.da
    # ENGLISH: Moreover, the hot-air heating system developed problems, making even operation itself problematic; as the machinery aged and hot air began to blow out, there was a brief but intense smell of oil.
    # CONFLICT: N1:열풍난방방식이(nsubj), N2:문제가(nsubj) under pred:'생겨 .saeng.gyeo' → default: N1(열풍난방방식이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0010-s54': [('deprel', 2, 'nsubj:outer')],

    # MH2_0010-s90 [test]
    # TEXT: 시계가 나쁘고 최대풍속이 초속 20미터가 넘더니 밤이 되어서야 겨우 수그러 들었다.
    # TRANSLIT: si.gye.ga na.bbeu.go choe.dae.pung.sog.i cho.sog 20.mi.teo.ga neom.deo.ni bam.i doe.eo.seo.ya gyeo.u su.geu.reo deul.eoss.da
    # ENGLISH: Visibility was poor and the maximum wind speed exceeded 20 m/s, but it finally eased by nightfall.
    # CONFLICT: N1:최대풍속이(nsubj), N2:20미터가(nsubj) under pred:'넘더니 .neom.deo.ni' → default: N1(최대풍속이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0010-s90': [('deprel', 3, 'nsubj:outer')],

    # MH2_0011-s10 [train]
    # TEXT: 선이 갖는 치료 효과가 정신의학계의 보고를 통하여 사실임이 확인된 것이다.
    # TRANSLIT: seon.i gaj.neun chi.ryo hyo.gwa.ga jeong.sin.yi.hag.gye.yi bo.go.reul tong.ha.yeo sa.sil.im.i hwag.in.doen geos.i.da
    # ENGLISH: It has been confirmed through reports in the psychiatric field that meditation has therapeutic effects.
    # CONFLICT: N1:효과가(nsubj), N2:사실임이(nsubj) under pred:'확인된 .hwag.in.doen' → default: N1(효과가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0011-s10': [('deprel', 4, 'nsubj:outer')],

    # MH2_0013-s107 [train]
    # TEXT: 기존의 생산관계가 생산력 발전을 저해하는 족쇄가 될 정도로 생산력과 생산관계관의 모순이 한계상황에 이르게 된 변혁의 객관적 조건을 뜻한다.
    # TRANSLIT: gi.jon.yi saeng.san.gwan.gye.ga saeng.san.ryeog bal.jeon.eul jeo.hae.ha.neun jog.swae.ga doel jeong.do.ro saeng.san.ryeog.gwa saeng.san.gwan.gye.gwan.yi mo.sun.i han.gye.sang.hwang.e i.reu.ge doen byeon.hyeog.yi gaeg.gwan.jeog jo.geon.eul ddeus.han.da
    # ENGLISH: The existing relations of production become shackles that impede the development of the productive forces.
    # CONFLICT: N1:생산관계가(nsubj), N2:족쇄가(csubj) under pred:'될 .doel' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0013-s107': [('deprel', 2, 'nsubj:outer')],

    # MH2_0013-s163 [train]
    # TEXT: 개신교 국가가 가톨릭 국가보다 자살률이 높고, 같은 나라라 하더라도 개신교 공동체가 가톨릭 공동체보다 자살률이 높다.
    # TRANSLIT: gae.sin.gyo gug.ga.ga ga.tol.rig gug.ga.bo.da ja.sal.ryul.i nop.go , gat.eun na.ra.ra ha.deo.ra.do gae.sin.gyo gong.dong.che.ga ga.tol.rig gong.dong.che.bo.da ja.sal.ryul.i nop.da
    # ENGLISH: Protestant countries have higher suicide rates than Catholic countries, and even within the same country Protestant communities have higher suicide rates than Catholic communities.
    # CONFLICT: N1:국가가(nsubj), N2:자살률이(nsubj) under pred:'높고 .nop.go' → default: N1(국가가)→nsubj:outer [NEEDS REVIEW]
    # CONFLICT: N1:공동체가(nsubj), N2:자살률이(nsubj) under pred:'높다 .nop.da' → default: N1(공동체가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0013-s163': [('deprel', 2, 'nsubj:outer'), ('deprel', 12, 'nsubj:outer')],

    # MH2_0013-s164 [train]
    # TEXT: 말하자면 개신교 공동체가 가톨릭 공동체보다 개인주의적이며 집단응집도가 낮다는 것이다.
    # TRANSLIT: mal.ha.ja.myeon gae.sin.gyo gong.dong.che.ga ga.tol.rig gong.dong.che.bo.da gae.in.ju.yi.jeog.i.myeo jib.dan.eung.jib.do.ga naj.da.neun geos.i.da
    # ENGLISH: In other words, Protestant communities are more individualistic than Catholic communities and have lower collective cohesion.
    # CONFLICT: N1:공동체가(nsubj), N2:집단응집도가(nsubj) under pred:'낮다는 .naj.da.neun' → default: N1(공동체가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0013-s164': [('deprel', 3, 'nsubj:outer')],

    # MH2_0013-s165 [train]
    # TEXT: 뿐만 아니라 일반적으로 가족이 있는 사람보다 독신자들이 자살률이 높다는 것이다.
    # TRANSLIT: bbun.man a.ni.ra il.ban.jeog.eu.ro ga.jog.i iss.neun sa.ram.bo.da dog.sin.ja.deul.i ja.sal.ryul.i nop.da.neun geos.i.da
    # ENGLISH: Moreover, in general, single people have higher suicide rates than people with families.
    # CONFLICT: N1:독신자들이(nsubj), N2:자살률이(nsubj) under pred:'높다는 .nop.da.neun' → default: N1(독신자들이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0013-s165': [('deprel', 7, 'nsubj:outer')],

    # MH2_0013-s77 [train]
    # TEXT: 변증법적 유물론은 물질의 존재론적 우선성은 수용하면서도 물질이 부동의 본질 존재가 아니라 끊임없이 운동하고 변화한다고 본다.
    # TRANSLIT: byeon.jeung.beob.jeog yu.mul.ron.eun mul.jil.yi jon.jae.ron.jeog u.seon.seong.eun su.yong.ha.myeon.seo.do mul.jil.i bu.dong.yi bon.jil jon.jae.ga a.ni.ra ggeunh.im.eobs.i un.dong.ha.go byeon.hwa.han.da.go bon.da
    # ENGLISH: The substance is not a form of existence.
    # CONFLICT: N1:물질이(nsubj), N2:존재가(csubj) under pred:'아니라 .a.ni.ra' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0013-s77': [('deprel', 7, 'nsubj:outer')],

    # MH2_0014-s150 [train]
    # TEXT: 무슨 책이든 그 책이 자신에게 유익이 되기 위해서는 무엇보다 먼저 관심이 있어야 하고, 재미를 느낄 수 있어야 한다.
    # TRANSLIT: mu.seun chaeg.i.deun geu chaeg.i ja.sin.e.ge yu.ig.i doe.gi wi.hae.seo.neun mu.eos.bo.da meon.jeo gwan.sim.i iss.eo.ya ha.go , jae.mi.reul neu.ggil su iss.eo.ya han.da
    # ENGLISH: Any book must first engage our interest and offer enjoyment if it is to be beneficial to us.
    # CONFLICT: N1:책이(nsubj), N2:유익이(csubj) under pred:'되기 .doe.gi' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0014-s150': [('deprel', 4, 'nsubj:outer')],

    # MH2_0014-s237 [train]
    # TEXT: 혹 전날밤의 노트가 오전 중의 작업을 위한 재료가 되어 있지 못할 때에는 곧장 밖으로 나갔다.
    # TRANSLIT: hog jeon.nal.bam.yi no.teu.ga o.jeon jung.yi jag.eob.eul wi.han jae.ryo.ga doe.eo iss.ji mos.hal ddae.e.neun god.jang bagg.eu.ro na.gass.da
    # ENGLISH: When the previous night's notes could not serve as material for the morning's work, he went straight outside.
    # CONFLICT: N1:노트가(nsubj), N2:재료가(csubj) under pred:'되어 .doe.eo' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0014-s237': [('deprel', 3, 'nsubj:outer')],

    # MH2_0014-s411 [train]
    # TEXT: 이렇게 일본의 신간들을 많이 구하는 것은 우선 번역을 믿을 수 있고, 또 책이 장정이나 내용이 잘 선택되어 있기 때문이다.
    # TRANSLIT: i.reoh.ge il.bon.yi sin.gan.deul.eul manh.i gu.ha.neun geos.eun u.seon beon.yeog.eul mid.eul su iss.go , ddo chaeg.i jang.jeong.i.na nae.yong.i jal seon.taeg.doe.eo iss.gi ddae.mun.i.da
    # ENGLISH: The reason we seek out many new Japanese publications is first that we can trust the translations, and also that the binding and content are well selected.
    # CONFLICT: N1:책이(nsubj), N2:장정이나(nsubj) under pred:'선택되어 .seon.taeg.doe.eo' → default: N1(책이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0014-s411': [('deprel', 14, 'nsubj:outer')],

    # MH2_0014-s441 [train]
    # TEXT: 외국의 경우 베스트 셀러가 고전이 된 예를 우리는 익히 알고 있다.
    # TRANSLIT: oe.gug.yi gyeong.u be.seu.teu sel.reo.ga go.jeon.i doen ye.reul u.ri.neun ig.hi al.go iss.da
    # ENGLISH: We are well aware of foreign examples where a bestseller has become a classic.
    # CONFLICT: N1:셀러가(nsubj), N2:고전이(csubj) under pred:'된 .doen' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0014-s441': [('deprel', 4, 'nsubj:outer')],

    # MH2_0014-s467 [train]
    # TEXT: 그러나 모든 책이 인생에 도움이 되는 것은 아니다.
    # TRANSLIT: geu.reo.na mo.deun chaeg.i in.saeng.e do.um.i doe.neun geos.eun a.ni.da
    # ENGLISH: However, not every book is beneficial to one's life.
    # CONFLICT: N1:책이(nsubj), N2:도움이(nsubj) under pred:'되는 .doe.neun' → default: N1(책이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0014-s467': [('deprel', 3, 'nsubj:outer')],

    # MH2_0014-s470 [train]
    # TEXT: 이렇게 말한 것은 책이 일종의 아편이 되어 버려, 그로 말미암아 현실 세계를 떠나 공상의 세계로 빠져들기 때문이다.
    # TRANSLIT: i.reoh.ge mal.han geos.eun chaeg.i il.jong.yi a.pyeon.i doe.eo beo.ryeo , geu.ro mal.mi.am.a hyeon.sil se.gye.reul ddeo.na gong.sang.yi se.gye.ro bba.jyeo.deul.gi ddae.mun.i.da
    # ENGLISH: The reason for saying this is that a book can become a kind of opium, causing one to leave the real world and sink into a world of fantasy.
    # CONFLICT: N1:책이(nsubj), N2:아편이(csubj) under pred:'되어 .doe.eo' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0014-s470': [('deprel', 4, 'nsubj:outer')],

    # MH2_0014-s475 [train]
    # TEXT: 또 한 가지, 독서가 작업의 하나가 될 수도 있다.
    # TRANSLIT: ddo han ga.ji , dog.seo.ga jag.eob.yi ha.na.ga doel su.do iss.da
    # ENGLISH: One more thing: reading itself can become a form of work.
    # CONFLICT: N1:독서가(nsubj), N2:하나가(csubj) under pred:'될 .doel' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0014-s475': [('deprel', 5, 'nsubj:outer')],

    # MH2_0014-s79 [train]
    # TEXT: 오늘의 독서는 독서 그 자체가 목적이 아니다.
    # TRANSLIT: o.neul.yi dog.seo.neun dog.seo geu ja.che.ga mog.jeog.i a.ni.da
    # ENGLISH: The thing itself is not the purpose.
    # CONFLICT: N1:자체가(nsubj), N2:목적이(nsubj) under pred:'아니다 .a.ni.da' → default: N1(자체가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0014-s79': [('deprel', 5, 'nsubj:outer')],

    # MH2_0014-s80 [train]
    # TEXT: 독서는 한낱 수단일 뿐 인간이 기계의 노예가 되는 것을 막고 인격을 완성하는 것이 궁극적인 목적인 것이다.
    # TRANSLIT: dog.seo.neun han.nat su.dan.il bbun in.gan.i gi.gye.yi no.ye.ga doe.neun geos.eul mag.go in.gyeog.eul wan.seong.ha.neun geos.i gung.geug.jeog.in mog.jeog.in geos.i.da
    # ENGLISH: A human being becomes a slave to machinery.
    # CONFLICT: N1:인간이(nsubj), N2:노예가(csubj) under pred:'되는 .doe.neun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0014-s80': [('deprel', 5, 'nsubj:outer')],

    # MH2_0017-s250 [train]
    # TEXT: 성실성이 구체적인 힘이 되어 환경에 새로운 조건을 추출케 하려면 과학적인 이법을 나의 것으로 마스터하는 노력이 또한 항시 병존하여야 한다.
    # TRANSLIT: seong.sil.seong.i gu.che.jeog.in him.i doe.eo hwan.gyeong.e sae.ro.un jo.geon.eul chu.chul.ke ha.ryeo.myeon gwa.hag.jeog.in i.beob.eul na.yi geos.eu.ro ma.seu.teo.ha.neun no.ryeog.i ddo.han hang.si byeong.jon.ha.yeo.ya han.da
    # ENGLISH: For sincerity to become a concrete force that extracts new conditions from the environment, one must always make the effort to master the scientific principles as one's own.
    # CONFLICT: N1:성실성이(nsubj), N2:힘이(nsubj) under pred:'되어 .doe.eo' → default: N1(성실성이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0017-s250': [('deprel', 1, 'nsubj:outer')],

    # MH2_0017-s63 [train]
    # TEXT: 그런데 그가 군현의 원이 되어 위세와 명성이 매우 자자했다.
    # TRANSLIT: geu.reon.de geu.ga gun.hyeon.yi weon.i doe.eo wi.se.wa myeong.seong.i mae.u ja.ja.haess.da
    # ENGLISH: And he became the magistrate of a county and was renowned for his authority and reputation.
    # CONFLICT: N1:그가(nsubj), N2:원이(nsubj) under pred:'되어 .doe.eo' → default: N1(그가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0017-s63': [('deprel', 2, 'nsubj:outer')],

    # MH2_0017-s76 [train]
    # TEXT: 옥중에 지리한 세월이 거연히 칠년이 된지라.
    # TRANSLIT: og.jung.e ji.ri.han se.weol.i geo.yeon.hi chil.nyeon.i doen.ji.ra
    # ENGLISH: The tedious years in prison had amounted to seven years.
    # CONFLICT: N1:세월이(nsubj), N2:칠년이(nsubj) under pred:'된지라 .doen.ji.ra' → default: N1(세월이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0017-s76': [('deprel', 3, 'nsubj:outer')],

    # MH2_0021-s118 [train]
    # TEXT: 오늘은 김영삼 대통령의 개혁의지가 용두사미가 되지 않기를 간절히 바라는 마음에서 몇 마디 하겠습니다.
    # TRANSLIT: o.neul.eun gim.yeong.sam dae.tong.ryeong.yi gae.hyeog.yi.ji.ga yong.du.sa.mi.ga doe.ji anh.gi.reul gan.jeol.hi ba.ra.neun ma.eum.e.seo myeoch ma.di ha.gess.seub.ni.da
    # ENGLISH: Today I would like to say a few words out of a fervent hope that President Kim Young-sam's will to reform does not fizzle out.
    # CONFLICT: N1:개혁의지가(nsubj), N2:용두사미가(csubj) under pred:'되지 .doe.ji' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0021-s118': [('deprel', 4, 'nsubj:outer')],

    # MH2_0021-s129 [train]
    # TEXT: 그러나 개혁이 용두사미가 되지 않을까 염려스럽습니다.
    # TRANSLIT: geu.reo.na gae.hyeog.i yong.du.sa.mi.ga doe.ji anh.eul.gga yeom.ryeo.seu.reob.seub.ni.da
    # ENGLISH: However, I am worried that the reform may fizzle out.
    # CONFLICT: N1:개혁이(nsubj), N2:용두사미가(csubj) under pred:'되지 .doe.ji' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0021-s129': [('deprel', 2, 'nsubj:outer')],

    # MH2_0021-s156 [train]
    # TEXT: 그리고 앞으로는 적어도 정치를 제대로 배우고 정치를 제대로 익힌 올바른 사람이 대한민국의 대통령이 되도록 우리 모두 합심하여 기도 해야 하겠습니다.
    # TRANSLIT: geu.ri.go ap.eu.ro.neun jeog.eo.do jeong.chi.reul je.dae.ro bae.u.go jeong.chi.reul je.dae.ro ig.hin ol.ba.reun sa.ram.i dae.han.min.gug.yi dae.tong.ryeong.i doe.do.rog u.ri mo.du hab.sim.ha.yeo gi.do hae.ya ha.gess.seub.ni.da
    # ENGLISH: In the future, we must all join together in prayer so that a truly qualified person who has properly learned and practiced politics becomes the President of the Republic of Korea.
    # CONFLICT: N1:사람이(nsubj), N2:대통령이(csubj) under pred:'되도록 .doe.do.rog' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0021-s156': [('deprel', 11, 'nsubj:outer')],

    # MH2_0021-s237 [train]
    # TEXT: 기독교인이 1천만명이나 된다는 우리 나라가 왜 무질서의 천국이 되었으며 왜 시한부 종말론자들의 온상이 되었습니까?
    # TRANSLIT: gi.dog.gyo.in.i 1.cheon.man.myeong.i.na doen.da.neun u.ri na.ra.ga wae mu.jil.seo.yi cheon.gug.i doe.eoss.eu.myeo wae si.han.bu jong.mal.ron.ja.deul.yi on.sang.i doe.eoss.seub.ni.gga ?
    # ENGLISH: Why has our country, which is said to have as many as ten million Christians, become a paradise of disorder and a breeding ground for doomsday cult members?
    # CONFLICT: N1:나라가(nsubj), N2:온상이(csubj) under pred:'되었습니까 .doe.eoss.seub.ni.gga' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0021-s237': [('deprel', 5, 'nsubj:outer')],

    # MH2_0021-s30 [train]
    # TEXT: 그래야 이번 14대 국회의원 선거가 정치개혁을 이루는 바람직한 선거가 될 수 있습니다.
    # TRANSLIT: geu.rae.ya i.beon 14.dae gug.hoe.yi.weon seon.geo.ga jeong.chi.gae.hyeog.eul i.ru.neun ba.ram.jig.han seon.geo.ga doel su iss.seub.ni.da
    # ENGLISH: Only then can the 14th general election become a desirable election that achieves political reform.
    # CONFLICT: N1:선거가(nsubj), N2:선거가(nsubj) under pred:'될 .doel' → default: N1(선거가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0021-s30': [('deprel', 5, 'nsubj:outer')],

    # MH2_0021-s310 [train]
    # TEXT: 하루 속히 일캐워야 정상을 되찾을 수 있는 사람이 한두 사람이 아닙니다.
    # TRANSLIT: ha.ru sog.hi il.kae.weo.ya jeong.sang.eul doe.chaj.eul su iss.neun sa.ram.i han.du sa.ram.i a.nib.ni.da
    # ENGLISH: There is no small number of people who need to be revived as quickly as possible in order to regain normality.
    # CONFLICT: N1:사람이(nsubj), N2:사람이(nsubj) under pred:'아닙니다 .a.nib.ni.da' → default: N1(사람이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0021-s310': [('deprel', 8, 'nsubj:outer')],

    # MH2_0021-s32 [train]
    # TEXT: 심지가 깊고 견고한 사람이 나라의 지도자가 되고 국회의원이 되어야 나라와 민족이 하나님의 평강으로 번영할 수 있습니다.
    # TRANSLIT: sim.ji.ga gip.go gyeon.go.han sa.ram.i na.ra.yi ji.do.ja.ga doe.go gug.hoe.yi.weon.i doe.eo.ya na.ra.wa min.jog.i ha.na.nim.yi pyeong.gang.eu.ro beon.yeong.hal su iss.seub.ni.da
    # ENGLISH: A person of deep conviction and steadfastness must become the nation's leader and a member of the National Assembly for the nation and people to prosper in God's peace.
    # CONFLICT: N1:사람이(nsubj), N2:국회의원이(csubj) under pred:'되어야 .doe.eo.ya' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0021-s32': [('deprel', 4, 'nsubj:outer')],

    # MH2_0021-s35 [train]
    # TEXT: 제 생각에는 첫째로 정직한 사람이 대통령이 되야겠습니다.
    # TRANSLIT: je saeng.gag.e.neun cheos.jjae.ro jeong.jig.han sa.ram.i dae.tong.ryeong.i doe.ya.gess.seub.ni.da
    # ENGLISH: In my view, the first requirement is that an honest person becomes president.
    # CONFLICT: N1:사람이(nsubj), N2:대통령이(csubj) under pred:'되야겠습니다 .doe.ya.gess.seub.ni.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0021-s35': [('deprel', 5, 'nsubj:outer')],

    # MH2_0021-s36 [train]
    # TEXT: 둘째로 법을 지키는 사람이 대통령이 돼야겠습니다.
    # TRANSLIT: dul.jjae.ro beob.eul ji.ki.neun sa.ram.i dae.tong.ryeong.i dwae.ya.gess.seub.ni.da
    # ENGLISH: Second, a person who upholds the law must become president.
    # CONFLICT: N1:사람이(nsubj), N2:대통령이(csubj) under pred:'돼야겠습니다 .dwae.ya.gess.seub.ni.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0021-s36': [('deprel', 4, 'nsubj:outer')],

    # MH2_0021-s37 [train]
    # TEXT: 법을 어기면서 금권타락선거를 조성하고 폭력을 앞세우는 사람이 대통령이 되면 앞으로 우리나라 꼴이 뭐가 되겠습니가?
    # TRANSLIT: beob.eul eo.gi.myeon.seo geum.gweon.ta.rag.seon.geo.reul jo.seong.ha.go pog.ryeog.eul ap.se.u.neun sa.ram.i dae.tong.ryeong.i doe.myeon ap.eu.ro u.ri.na.ra ggol.i mweo.ga doe.gess.seub.ni.ga ?
    # ENGLISH: If a person who breaks the law, fosters money-driven corrupt elections, and leads with violence becomes president, what will become of our country in the future?
    # CONFLICT: N1:사람이(nsubj), N2:대통령이(csubj) under pred:'되면 .doe.myeon' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    # CONFLICT: N1:꼴이(nsubj), N2:뭐가(csubj) under pred:'되겠습니가 .doe.gess.seub.ni.ga' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0021-s37': [('deprel', 7, 'nsubj:outer'), ('deprel', 12, 'nsubj:outer')],

    # MH2_0021-s371 [train]
    # TEXT: 무조건 먹이는 것만이 능사가 아닙니다.
    # TRANSLIT: mu.jo.geon meog.i.neun geos.man.i neung.sa.ga a.nib.ni.da
    # ENGLISH: Feeding unconditionally is not the only answer.
    # CONFLICT: N1:것만이(nsubj), N2:능사가(nsubj) under pred:'아닙니다 .a.nib.ni.da' → default: N1(것만이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0021-s371': [('deprel', 3, 'nsubj:outer')],

    # MH2_0021-s38 [train]
    # TEXT: 셋째로 국민을 생각하는 사람이 대통령이 돼야겠습니다.
    # TRANSLIT: ses.jjae.ro gug.min.eul saeng.gag.ha.neun sa.ram.i dae.tong.ryeong.i dwae.ya.gess.seub.ni.da
    # ENGLISH: Third, a person who thinks of the people must become president.
    # CONFLICT: N1:사람이(nsubj), N2:대통령이(csubj) under pred:'돼야겠습니다 .dwae.ya.gess.seub.ni.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0021-s38': [('deprel', 4, 'nsubj:outer')],

    # MH2_0021-s41 [train]
    # TEXT: 넷째로 헛소리를 하지 않는 사람이 대통령이 돼야겠습니다.
    # TRANSLIT: nes.jjae.ro heos.so.ri.reul ha.ji anh.neun sa.ram.i dae.tong.ryeong.i dwae.ya.gess.seub.ni.da
    # ENGLISH: Fourth, a person who does not talk nonsense must become president.
    # CONFLICT: N1:사람이(nsubj), N2:대통령이(csubj) under pred:'돼야겠습니다 .dwae.ya.gess.seub.ni.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0021-s41': [('deprel', 5, 'nsubj:outer')],

    # MH2_0021-s43 [train]
    # TEXT: 우리 정부의 능력으로는 도저히 할 수 없는 일도 해낼 수 있다고 말도 안되는 헛소리를 하는 사람이 대통령이 돼서 되겠습니까?
    # TRANSLIT: u.ri jeong.bu.yi neung.ryeog.eu.ro.neun do.jeo.hi hal su eobs.neun il.do hae.nael su iss.da.go mal.do an.doe.neun heos.so.ri.reul ha.neun sa.ram.i dae.tong.ryeong.i dwae.seo doe.gess.seub.ni.gga ?
    # ENGLISH: Can a person who talks absurd nonsense, claiming to accomplish things that our government is utterly incapable of, become president?
    # CONFLICT: N1:사람이(nsubj), N2:대통령이(csubj) under pred:'돼서 .dwae.seo' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0021-s43': [('deprel', 16, 'nsubj:outer')],

    # MH2_0021-s45 [train]
    # TEXT: 다섯째 중소기업을 육성할 수 있는 사람이 대통령이 돼야겠습니다.
    # TRANSLIT: da.seos.jjae jung.so.gi.eob.eul yug.seong.hal su iss.neun sa.ram.i dae.tong.ryeong.i dwae.ya.gess.seub.ni.da
    # ENGLISH: Fifth, a person capable of nurturing small and medium enterprises must become president.
    # CONFLICT: N1:사람이(nsubj), N2:대통령이(csubj) under pred:'돼야겠습니다 .dwae.ya.gess.seub.ni.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0021-s45': [('deprel', 6, 'nsubj:outer')],

    # MH2_0021-s50 [train]
    # TEXT: 끝으로 그 무엇보다 개혁의지가 확실한 사람이 대통령이 돼야겠습니다.
    # TRANSLIT: ggeut.eu.ro geu mu.eos.bo.da gae.hyeog.yi.ji.ga hwag.sil.han sa.ram.i dae.tong.ryeong.i dwae.ya.gess.seub.ni.da
    # ENGLISH: Finally, above all else, a person with a firm commitment to reform must become president.
    # CONFLICT: N1:사람이(nsubj), N2:대통령이(nsubj) under pred:'돼야겠습니다 .dwae.ya.gess.seub.ni.da' → default: N1(사람이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0021-s50': [('deprel', 6, 'nsubj:outer')],

    # MH2_0021-s52 [train]
    # TEXT: 부정부패가 사회 곳곳에 만여돼 있기 때문에 부정부패를 과감하게 척결할 수 있는 개혁자가 대통령이 돼야겠습니다.
    # TRANSLIT: bu.jeong.bu.pae.ga sa.hoe gos.gos.e man.yeo.dwae iss.gi ddae.mun.e bu.jeong.bu.pae.reul gwa.gam.ha.ge cheog.gyeol.hal su iss.neun gae.hyeog.ja.ga dae.tong.ryeong.i dwae.ya.gess.seub.ni.da
    # ENGLISH: Because corruption is rampant throughout society, a reformer capable of boldly eradicating it must become president.
    # CONFLICT: N1:개혁자가(nsubj), N2:대통령이(csubj) under pred:'돼야겠습니다 .dwae.ya.gess.seub.ni.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0021-s52': [('deprel', 12, 'nsubj:outer')],

    # MH2_0021-s67 [train]
    # TEXT: 상식에서 벗어난 사람이 어떻게 좋은 대통령이 될 수 있겠습니까?
    # TRANSLIT: sang.sig.e.seo beos.eo.nan sa.ram.i eo.ddeoh.ge joh.eun dae.tong.ryeong.i doel su iss.gess.seub.ni.gga ?
    # ENGLISH: How can someone who has departed from common sense become a good president?
    # CONFLICT: N1:사람이(nsubj), N2:대통령이(csubj) under pred:'될 .doel' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0021-s67': [('deprel', 3, 'nsubj:outer')],

    # MH2_0024-s186 [train]
    # TEXT: 이것이 바로 역사적 비평과 전기적 비평이 공존해야 하는 이유가 된다.
    # TRANSLIT: i.geos.i ba.ro yeog.sa.jeog bi.pyeong.gwa jeon.gi.jeog bi.pyeong.i gong.jon.hae.ya ha.neun i.yu.ga doen.da
    # ENGLISH: This is precisely the reason that historical criticism and biographical criticism must coexist.
    # CONFLICT: N1:이것이(nsubj), N2:이유가(csubj) under pred:'된다 .doen.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0024-s186': [('deprel', 1, 'nsubj:outer')],

    # MH2_0024-s199 [train]
    # TEXT: 쌩뜨뵈브가 여기서 밝히는 것은 그의 전기적 방법이 개인 위주가 아니라 사회적이라는 것이다.
    # TRANSLIT: ssaeng.ddeu.boe.beu.ga yeo.gi.seo barg.hi.neun geos.eun geu.yi jeon.gi.jeog bang.beob.i gae.in wi.ju.ga a.ni.ra sa.hoe.jeog.i.ra.neun geos.i.da
    # ENGLISH: What Sainte-Beuve reveals here is that his biographical method is social rather than focused on the individual.
    # CONFLICT: N1:방법이(nsubj), N2:위주가(nsubj) under pred:'아니라 .a.ni.ra' → default: N1(방법이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0024-s199': [('deprel', 7, 'nsubj:outer')],

    # MH2_0024-s29 [train]
    # TEXT: 이러한 여러가지 난점을 극복하고 말이나 글의 진정한 의미를 찾아내고 이를 다시 독자에게 알려주는 일이 해석의 사명이 되어야 할 것이다.
    # TRANSLIT: i.reo.han yeo.reo.ga.ji nan.jeom.eul geug.bog.ha.go mal.i.na geul.yi jin.jeong.han yi.mi.reul chaj.a.nae.go i.reul da.si dog.ja.e.ge al.ryeo.ju.neun il.i hae.seog.yi sa.myeong.i doe.eo.ya hal geos.i.da
    # ENGLISH: Overcoming these various difficulties and finding the true meaning of words and texts, then conveying this meaning to readers, must be the mission of interpretation.
    # CONFLICT: N1:일이(nsubj), N2:사명이(nsubj) under pred:'되어야 .doe.eo.ya' → default: N1(일이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0024-s29': [('deprel', 14, 'nsubj:outer')],

    # MH2_0024-s324 [train]
    # TEXT: 이에 대하여 웰렉과 웨렌은 문학적 전기가 일반 역사서와 방법론적 차이가 없다면 그것은 단순한 역사서에 불과한 것이 된다고 지적한다.
    # TRANSLIT: i.e dae.ha.yeo wel.reg.gwa we.ren.eun mun.hag.jeog jeon.gi.ga il.ban yeog.sa.seo.wa bang.beob.ron.jeog cha.i.ga eobs.da.myeon geu.geos.eun dan.sun.han yeog.sa.seo.e bul.gwa.han geos.i doen.da.go ji.jeog.han.da
    # ENGLISH: In response, Wellek and Warren point out that if literary biography does not differ methodologically from general historiography, it becomes mere historiography.
    # CONFLICT: N1:전기가(nsubj), N2:차이가(nsubj) under pred:'없다면 .eobs.da.myeon' → default: N1(전기가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0024-s324': [('deprel', 6, 'nsubj:outer')],

    # MH2_0024-s47 [train]
    # TEXT: 그들이 재조직되어서 하나의 통일체가 되었을 때 처음으로 완전한 의미를 표현하고 이해하게 된다.
    # TRANSLIT: geu.deul.i jae.jo.jig.doe.eo.seo ha.na.yi tong.il.che.ga doe.eoss.eul ddae cheo.eum.eu.ro wan.jeon.han yi.mi.reul pyo.hyeon.ha.go i.hae.ha.ge doen.da
    # ENGLISH: Only when they are reorganized into a unified whole does one first express and understand their complete meaning.
    # CONFLICT: N1:그들이(nsubj), N2:통일체가(csubj) under pred:'되었을 .doe.eoss.eul' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0024-s47': [('deprel', 1, 'nsubj:outer')],

    # MH2_0026-s71 [train]
    # TEXT: 하지만 空間과 精神이 서로 영향을 주고 받은 흔적이 바탕이 되어 있기에 깊이와 무게를 느낄 수 있는 것이다.
    # TRANSLIT: ha.ji.man kōngjiān.gwa jīngshén.i seo.ro yeong.hyang.eul ju.go bad.eun heun.jeog.i ba.tang.i doe.eo iss.gi.e gip.i.wa mu.ge.reul neu.ggil su iss.neun geos.i.da
    # ENGLISH: However, because the traces of mutual influence between space and spirit form the foundation, one can feel depth and weight.
    # CONFLICT: N1:흔적이(nsubj), N2:바탕이(csubj) under pred:'되어 .doe.eo' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0026-s71': [('deprel', 8, 'nsubj:outer')],

    # MH2_0028-s76 [train]
    # TEXT: 기질 또한 우리와 어찌나 닮았던지 조사단원 모두가 놀란 일이 한두 번이 아니다.
    # TRANSLIT: gi.jil ddo.han u.ri.wa eo.jji.na darm.ass.deon.ji jo.sa.dan.weon mo.du.ga nol.ran il.i han.du beon.i a.ni.da
    # ENGLISH: Their temperament also resembled ours so closely that every member of the survey team was surprised more than once or twice.
    # CONFLICT: N1:일이(nsubj), N2:번이(csubj) under pred:'아니다 .a.ni.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0028-s76': [('deprel', 9, 'nsubj:outer')],

    # MH2_0028-s83 [train]
    # TEXT: 우리와 몽골과의 문화 교류는 저들의 침략이 계기가 되어 더욱 활발하게 이루어졌다.
    # TRANSLIT: u.ri.wa mong.gol.gwa.yi mun.hwa gyo.ryu.neun jeo.deul.yi chim.ryag.i gye.gi.ga doe.eo deo.ug hwal.bal.ha.ge i.ru.eo.jyeoss.da
    # ENGLISH: Cultural exchange between Korea and Mongolia was further invigorated as a result of their invasions.
    # CONFLICT: N1:침략이(nsubj), N2:계기가(nsubj) under pred:'되어 .doe.eo' → default: N1(침략이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0028-s83': [('deprel', 6, 'nsubj:outer')],

    # MH2_0031-s121 [train]
    # TEXT: 아니, 그 자체가 사회주의내의 부르조아적 권리가 아닌가.
    # TRANSLIT: a.ni , geu ja.che.ga sa.hoe.ju.yi.nae.yi bu.reu.jo.a.jeog gweon.ri.ga a.nin.ga
    # ENGLISH: Indeed, is that not itself a bourgeois right within socialism?
    # CONFLICT: N1:자체가(nsubj), N2:권리가(nsubj) under pred:'아닌가 .a.nin.ga' → default: N1(자체가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0031-s121': [('deprel', 4, 'nsubj:outer')],

    # MH2_0031-s125 [train]
    # TEXT: 그 자체가 사회의 경제제도의 불완전성을 표현하는 자연적인 파생물이 아닌가.
    # TRANSLIT: geu ja.che.ga sa.hoe.yi gyeong.je.je.do.yi bul.wan.jeon.seong.eul pyo.hyeon.ha.neun ja.yeon.jeog.in pa.saeng.mul.i a.nin.ga
    # ENGLISH: Is it not itself a natural by-product expressing the imperfection of society's economic system?
    # CONFLICT: N1:자체가(nsubj), N2:파생물이(nsubj) under pred:'아닌가 .a.nin.ga' → default: N1(자체가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0031-s125': [('deprel', 2, 'nsubj:outer')],

    # MH2_0031-s307 [train]
    # TEXT: 계급존재가 사멸되어 그 투쟁이 없어진 이상 정치적 지배가 무슨 필요가 있는가?
    # TRANSLIT: gye.geub.jon.jae.ga sa.myeol.doe.eo geu tu.jaeng.i eobs.eo.jin i.sang jeong.chi.jeog ji.bae.ga mu.seun pil.yo.ga iss.neun.ga ?
    # ENGLISH: Given that class existence has withered away and its struggle ceased, what need is there for political domination?
    # CONFLICT: N1:지배가(nsubj), N2:필요가(nsubj) under pred:'있는가 .iss.neun.ga' → default: N1(지배가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0031-s307': [('deprel', 8, 'nsubj:outer')],

    # MH2_0032-s121 [train]
    # TEXT: 쟝세니스트들은 그들이 정죄하는 세상에서 벗어날 길이 없이 신앙과 양립되지 않는 악의 세상에 살아야 한다는 것이 바로 직면한 딜레마가 된다.
    # TRANSLIT: jyang.se.ni.seu.teu.deul.eun geu.deul.i jeong.joe.ha.neun se.sang.e.seo beos.eo.nal gil.i eobs.i sin.ang.gwa yang.rib.doe.ji anh.neun ag.yi se.sang.e sal.a.ya han.da.neun geos.i ba.ro jig.myeon.han dil.re.ma.ga doen.da
    # ENGLISH: The Jansenists face the dilemma of having to live in a sinful world incompatible with faith, with no way to escape the world they condemn.
    # CONFLICT: N1:것이(nsubj), N2:딜레마가(csubj) under pred:'된다 .doen.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0032-s121': [('deprel', 15, 'nsubj:outer')],

    # MH2_0032-s33 [train]
    # TEXT: 즉 누이의 죽음이 중심적 진원이 된 감정의 복합적인 망과 그 표현을 분석해야 할 것이다라고 그는 설명한다.
    # TRANSLIT: jeug nu.i.yi jug.eum.i jung.sim.jeog jin.weon.i doen gam.jeong.yi bog.hab.jeog.in mang.gwa geu pyo.hyeon.eul bun.seog.hae.ya hal geos.i.da.ra.go geu.neun seol.myeong.han.da
    # ENGLISH: That is, as he explains, one must analyze the complex web of emotions and their expression centered on his sister's death.
    # CONFLICT: N1:죽음이(nsubj), N2:진원이(csubj) under pred:'된 .doen' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0032-s33': [('deprel', 3, 'nsubj:outer')],

    # MH2_0034-s80 [train]
    # TEXT: 적지 않은 신자들이 예수 그리스도의 복음을 믿는 것이 곧 인생의 모든 일에 만사형통하기 위해 하나님께 비는 것으로 생각하고 있다.
    # TRANSLIT: jeog.ji anh.eun sin.ja.deul.i ye.su geu.ri.seu.do.yi bog.eum.eul mid.neun geos.i god in.saeng.yi mo.deun il.e man.sa.hyeong.tong.ha.gi wi.hae ha.na.nim.gge bi.neun geos.eu.ro saeng.gag.ha.go iss.da
    # ENGLISH: Quite a few believers think that having faith in the gospel of Jesus Christ means praying to God for everything in life to go smoothly.
    # CONFLICT: N1:신자들이(nsubj), N2:것이(nsubj) under pred:'생각하고 .saeng.gag.ha.go' → default: N1(신자들이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0034-s80': [('deprel', 3, 'nsubj:outer')],

    # MH2_0035-s115 [train]
    # TEXT: 여기서 우리는 같은 교리가 한쪽에서는 건강한 도덕적 갱생의 동기가 되고, 반대로 다른 쪽에서는 도덕적 파산의 길잡이가 된다는 사실을 보게 된다.
    # TRANSLIT: yeo.gi.seo u.ri.neun gat.eun gyo.ri.ga han.jjog.e.seo.neun geon.gang.han do.deog.jeog gaeng.saeng.yi dong.gi.ga doe.go , ban.dae.ro da.reun jjog.e.seo.neun do.deog.jeog pa.san.yi gil.jab.i.ga doen.da.neun sa.sil.eul bo.ge doen.da
    # ENGLISH: Here we see the fact that the same doctrine becomes the motivation for healthy moral regeneration on one side, and conversely a guide to moral bankruptcy on the other.
    # CONFLICT: N1:교리가(nsubj), N2:길잡이가(nsubj) under pred:'된다는 .doen.da.neun' → default: N1(교리가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0035-s115': [('deprel', 4, 'nsubj:outer')],

    # MH2_0035-s130 [train]
    # TEXT: 그것이 간접적인 이유가 될 수는 있다.
    # TRANSLIT: geu.geos.i gan.jeob.jeog.in i.yu.ga doel su.neun iss.da
    # ENGLISH: It can serve as an indirect reason.
    # CONFLICT: N1:그것이(nsubj), N2:이유가(nsubj) under pred:'될 .doel' → default: N1(그것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0035-s130': [('deprel', 1, 'nsubj:outer')],

    # MH2_0035-s36 [train]
    # TEXT: 기복행위가 무엇이 문제인지 구체적인 실례를 들어보기로 하자.
    # TRANSLIT: gi.bog.haeng.wi.ga mu.eos.i mun.je.in.ji gu.che.jeog.in sil.rye.reul deul.eo.bo.gi.ro ha.ja
    # ENGLISH: Let us give concrete examples of what the problem is with fortune-seeking behavior.
    # CONFLICT: N1:기복행위가(nsubj), N2:무엇이(nsubj) under pred:'문제인지 .mun.je.in.ji' → default: N1(기복행위가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0035-s36': [('deprel', 1, 'nsubj:outer')],

    # MH2_0035-s46 [train]
    # TEXT: 아마도 그들이 자식에게 대한 정성이 그만큼 각별했기 때문에 그들의 행위에 아무런 잘못이 없다고 말할 사람들도 있을 것이다.
    # TRANSLIT: a.ma.do geu.deul.i ja.sig.e.ge dae.han jeong.seong.i geu.man.keum gag.byeol.haess.gi ddae.mun.e geu.deul.yi haeng.wi.e a.mu.reon jal.mos.i eobs.da.go mal.hal sa.ram.deul.do iss.eul geos.i.da
    # ENGLISH: There will perhaps be those who say that because their devotion to their children was so exceptional, there was nothing wrong with their actions.
    # CONFLICT: N1:그들이(nsubj), N2:정성이(nsubj) under pred:'각별했기 .gag.byeol.haess.gi' → default: N1(그들이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0035-s46': [('deprel', 2, 'nsubj:outer')],

    # MH2_0035-s461 [train]
    # TEXT: 오히려 모든 사람이 신 앞에서 사제가 된다는 만인사제론의 입장을 갖는다.
    # TRANSLIT: o.hi.ryeo mo.deun sa.ram.i sin ap.e.seo sa.je.ga doen.da.neun man.in.sa.je.ron.yi ib.jang.eul gaj.neun.da
    # ENGLISH: Rather, one takes the position of universal priesthood — that all people become priests before God.
    # CONFLICT: N1:사람이(nsubj), N2:사제가(nsubj) under pred:'된다는 .doen.da.neun' → default: N1(사람이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0035-s461': [('deprel', 3, 'nsubj:outer')],

    # MH2_0035-s62 [train]
    # TEXT: 그러나 그 품위를 유지한다는 것이 어느 시대 어느 사회에서나 그리 쉬운 일이 아니었다.
    # TRANSLIT: geu.reo.na geu pum.wi.reul yu.ji.han.da.neun geos.i eo.neu si.dae eo.neu sa.hoe.e.seo.na geu.ri swi.un il.i a.ni.eoss.da
    # ENGLISH: However, maintaining that dignity has not been so easy in any era or any society.
    # CONFLICT: N1:것이(nsubj), N2:일이(nsubj) under pred:'아니었다 .a.ni.eoss.da' → default: N1(것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0035-s62': [('deprel', 5, 'nsubj:outer')],

    # MH2_0035-s67 [train]
    # TEXT: 바꾸어 말한다면, 인간이 자신의 욕망을 어느 선에서 얼마나 절제할 수 있는 훈련이 되었는가의 정도에 달려 있다.
    # TRANSLIT: ba.ggu.eo mal.han.da.myeon , in.gan.i ja.sin.yi yog.mang.eul eo.neu seon.e.seo eol.ma.na jeol.je.hal su iss.neun hun.ryeon.i doe.eoss.neun.ga.yi jeong.do.e dal.ryeo iss.da
    # ENGLISH: In other words, it depends on the degree to which a person has been trained in restraining their desires at a certain limit.
    # CONFLICT: N1:인간이(nsubj), N2:훈련이(nsubj) under pred:'되었는가의 .doe.eoss.neun.ga.yi' → default: N1(인간이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0035-s67': [('deprel', 4, 'nsubj:outer')],

    # MH2_0035-s89 [train]
    # TEXT: 흔히 특정한 종교집단의 교리가 일반사회의 상식으로 납득이 가지 않을 때 그를 사교라고 하는 경우가 많다.
    # TRANSLIT: heun.hi teug.jeong.han jong.gyo.jib.dan.yi gyo.ri.ga il.ban.sa.hoe.yi sang.sig.eu.ro nab.deug.i ga.ji anh.eul ddae geu.reul sa.gyo.ra.go ha.neun gyeong.u.ga manh.da
    # ENGLISH: Often when the doctrines of a particular religious group are incomprehensible to general social common sense, it is frequently called a cult.
    # CONFLICT: N1:교리가(nsubj), N2:납득이(nsubj) under pred:'가지 .ga.ji' → default: N1(교리가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0035-s89': [('deprel', 4, 'nsubj:outer')],

    # MH2_0037-s14 [train]
    # TEXT: 동물이 소년 소녀의 성장과 무슨 직접적인 관계가 있겠습니까?
    # TRANSLIT: dong.mul.i so.nyeon so.nyeo.yi seong.jang.gwa mu.seun jig.jeob.jeog.in gwan.gye.ga iss.gess.seub.ni.gga ?
    # ENGLISH: What direct relationship could animals have with the growth of boys and girls?
    # CONFLICT: N1:동물이(nsubj), N2:성장과(nsubj) under pred:'있겠습니까 .iss.gess.seub.ni.gga' → default: N1(동물이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0037-s14': [('deprel', 1, 'nsubj:outer')],

    # MH2_0037-s192 [train]
    # TEXT: 그것이 동화를 동화답게 전달하는 길이 아닌가 생각됩니다.
    # TRANSLIT: geu.geos.i dong.hwa.reul dong.hwa.dab.ge jeon.dal.ha.neun gil.i a.nin.ga saeng.gag.doeb.ni.da
    # ENGLISH: Is this not the way to convey fairy tales in a truly fairy-tale manner?
    # CONFLICT: N1:그것이(nsubj), N2:길이(csubj) under pred:'아닌가 .a.nin.ga' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0037-s192': [('deprel', 1, 'nsubj:outer')],

    # MH2_0037-s219 [train]
    # TEXT: 이야기판이 부디 치유와 재생의 자리가 되게 하십시오.
    # TRANSLIT: i.ya.gi.pan.i bu.di chi.yu.wa jae.saeng.yi ja.ri.ga doe.ge ha.sib.si.o
    # ENGLISH: Please let this storytelling space become a place of healing and regeneration.
    # CONFLICT: N1:이야기판이(nsubj), N2:자리가(nsubj) under pred:'되게 .doe.ge' → default: N1(이야기판이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0037-s219': [('deprel', 1, 'nsubj:outer')],

    # MH2_0037-s305 [train]
    # TEXT: 하늘에서 내리는 눈과 사물을 보는 눈이 서로 뜻은 다르나 발음이 같은 것을 기회로 삼아서 익살을 부린 보기입니다.
    # TRANSLIT: ha.neul.e.seo nae.ri.neun nun.gwa sa.mul.eul bo.neun nun.i seo.ro ddeus.eun da.reu.na bal.eum.i gat.eun geos.eul gi.hoe.ro sam.a.seo ig.sal.eul bu.rin bo.gi.ib.ni.da
    # ENGLISH: This is an example of humor using as an opportunity the fact that "snow falling from the sky" and "eyes that see things" differ in meaning but share the same pronunciation.
    # CONFLICT: N1:눈과(nsubj), N2:발음이(nsubj) under pred:'같은 .gat.eun' → default: N1(눈과)→nsubj:outer [NEEDS REVIEW]
    'MH2_0037-s305': [('deprel', 3, 'nsubj:outer')],

    # MH2_0037-s326 [train]
    # TEXT: 아이가 동화로 인해 비로소 처음으로 '세계인' 이 된다고 해도 지나친 말은 아닙니다.
    # TRANSLIT: a.i.ga dong.hwa.ro in.hae bi.ro.so cheo.eum.eu.ro ' se.gye.in ' i doen.da.go hae.do ji.na.chin mal.eun a.nib.ni.da
    # ENGLISH: It would not be an overstatement to say that through fairy tales a child becomes a "world citizen" for the very first time.
    # CONFLICT: N1:아이가(nsubj), N2:세계인(nsubj) under pred:'된다고 .doen.da.go' → default: N1(아이가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0037-s326': [('deprel', 1, 'nsubj:outer')],

    # MH2_0037-s434 [train]
    # TEXT: 전자가 음지가 양지가 되는 사이에 후자는 양지가 음지로 바뀌게 되는 것입니다.
    # TRANSLIT: jeon.ja.ga eum.ji.ga yang.ji.ga doe.neun sa.i.e hu.ja.neun yang.ji.ga eum.ji.ro ba.ggwi.ge doe.neun geos.ib.ni.da
    # ENGLISH: While the former transforms from shadow into light, the latter changes from light into shadow.
    # CONFLICT: N1:전자가(nsubj), N2:음지가(nsubj), N3:양지가(nsubj) under pred:'되는 .doe.neun' → 3-way default: N1,N2→nsubj:outer [NEEDS REVIEW]
    'MH2_0037-s434': [('deprel', 1, 'nsubj:outer'), ('deprel', 2, 'nsubj:outer')],

    # MH2_0037-s512 [train]
    # TEXT: 교활하고 냉혹하며 으시시하고 음흉한 것이 대체로 동화 속의 할머니와는 너무나 다른 할머니가 동화에는 등장합니다.
    # TRANSLIT: gyo.hwal.ha.go naeng.hog.ha.myeo eu.si.si.ha.go eum.hyung.han geos.i dae.che.ro dong.hwa sog.yi hal.meo.ni.wa.neun neo.mu.na da.reun hal.meo.ni.ga dong.hwa.e.neun deung.jang.hab.ni.da
    # ENGLISH: A grandmother who is cunning, cold-hearted, eerie, and sinister — utterly unlike the typical grandmother in fairy tales — appears in fairy tales.
    # CONFLICT: N1:것이(nsubj), N2:할머니가(nsubj) under pred:'등장합니다 .deung.jang.hab.ni.da' → default: N1(것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0037-s512': [('deprel', 5, 'nsubj:outer')],

    # MH2_0042-s110 [train]
    # TEXT: 못내 아르바이트를 중단하고 말았지만, 1년여를 버티면서 모은 돈이 이자를 합하여 1천 1백 10만 원이 되었다.
    # TRANSLIT: mos.nae a.reu.ba.i.teu.reul jung.dan.ha.go mal.ass.ji.man , 1.nyeon.yeo.reul beo.ti.myeon.seo mo.eun don.i i.ja.reul hab.ha.yeo 1.cheon 1.baeg 10.man weon.i doe.eoss.da
    # ENGLISH: Though I eventually had to give up my part-time work, the money saved while holding out for about a year, combined with interest, came to 11.1 million won.
    # CONFLICT: N1:돈이(nsubj), N2:원이(nsubj) under pred:'되었다 .doe.eoss.da' → default: N1(돈이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0042-s110': [('deprel', 9, 'nsubj:outer')],

    # MH2_0042-s135 [train]
    # TEXT: 귀하가 이상과 같은 결론을 내리고 있을 때 근사한 이야기 하나가 들어왔다.
    # TRANSLIT: gwi.ha.ga i.sang.gwa gat.eun gyeol.ron.eul nae.ri.go iss.eul ddae geun.sa.han i.ya.gi ha.na.ga deul.eo.wass.da
    # ENGLISH: When you were drawing the above conclusions, an interesting story came in.
    # CONFLICT: N1:귀하가(nsubj), N2:하나가(nsubj) under pred:'들어왔다 .deul.eo.wass.da' → default: N1(귀하가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0042-s135': [('deprel', 1, 'nsubj:outer')],

    # MH2_0042-s15 [train]
    # TEXT: 이 1만 원 지폐 300장이 귀하의 전재산이고 종자돈이 된다.
    # TRANSLIT: i 1.man weon ji.pye 300.jang.i gwi.ha.yi jeon.jae.san.i.go jong.ja.don.i doen.da
    # ENGLISH: These 300 bills of 10,000 won become your entire fortune and seed money.
    # CONFLICT: N1:300장이(nsubj), N2:종자돈이(nsubj) under pred:'된다 .doen.da' → default: N1(300장이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0042-s15': [('deprel', 5, 'nsubj:outer')],

    # MH2_0042-s183 [train]
    # TEXT: 그가 가르쳐 준 종목이 실제로 가격이 오르면 따로 성공 보수를 지불하겠다는 약속도 덧붙였다.
    # TRANSLIT: geu.ga ga.reu.chyeo jun jong.mog.i sil.je.ro ga.gyeog.i o.reu.myeon dda.ro seong.gong bo.su.reul ji.bul.ha.gess.da.neun yag.sog.do deos.but.yeoss.da
    # ENGLISH: He also added a promise to pay a separate success fee if the stock he recommended actually rose in price.
    # CONFLICT: N1:종목이(nsubj), N2:가격이(nsubj) under pred:'오르면 .o.reu.myeon' → default: N1(종목이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0042-s183': [('deprel', 4, 'nsubj:outer')],

    # MH2_0042-s200 [train]
    # TEXT: 아침 일찍 일어나 밤 늦게까지 뛰어다닌 그 동안의 생활이 헛수고가 아니었다고 생각하니 스스로 돌이켜보아도 대견스러웠다.
    # TRANSLIT: a.chim il.jjig il.eo.na bam neuj.ge.gga.ji ddwi.eo.da.nin geu dong.an.yi saeng.hwal.i heos.su.go.ga a.ni.eoss.da.go saeng.gag.ha.ni seu.seu.ro dol.i.kyeo.bo.a.do dae.gyeon.seu.reo.weoss.da
    # ENGLISH: Thinking that the life of getting up early and running around until late at night had not been in vain, I felt proud even looking back at myself.
    # CONFLICT: N1:생활이(nsubj), N2:헛수고가(nsubj) under pred:'아니었다고 .a.ni.eoss.da.go' → default: N1(생활이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0042-s200': [('deprel', 9, 'nsubj:outer')],

    # MH2_0042-s23 [train]
    # TEXT: 귀하가 그 무용담의 주인공이 되지 말라는 법은 이 세상 어디에도 없다.
    # TRANSLIT: gwi.ha.ga geu mu.yong.dam.yi ju.in.gong.i doe.ji mal.ra.neun beob.eun i se.sang eo.di.e.do eobs.da
    # ENGLISH: There is no rule anywhere in this world that says you cannot become the protagonist of such a heroic tale.
    # CONFLICT: N1:귀하가(nsubj), N2:주인공이(nsubj) under pred:'되지 .doe.ji' → default: N1(귀하가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0042-s23': [('deprel', 1, 'nsubj:outer')],

    # MH2_0042-s246 [train]
    # TEXT: 투자가 모두가 사자고 달려들 때는 천정세, 역으로 너도 나도 팔자고 보유 주식을 시장에 내놓으면 바닥세가 되고 만다.
    # TRANSLIT: tu.ja.ga mo.du.ga sa.ja.go dal.ryeo.deul ddae.neun cheon.jeong.se , yeog.eu.ro neo.do na.do pal.ja.go bo.yu ju.sig.eul si.jang.e nae.noh.eu.myeon ba.dag.se.ga doe.go man.da
    # ENGLISH: When all investors rush in to buy, it becomes a ceiling market; conversely, when everyone puts their stocks on the market to sell, it becomes a floor market.
    # CONFLICT: N1:투자가(nsubj), N2:모두가(nsubj) under pred:'달려들 .dal.ryeo.deul' → default: N1(투자가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0042-s246': [('deprel', 1, 'nsubj:outer')],

    # MH2_0042-s319 [train]
    # TEXT: 귀하는 자금이 2천만 원이 될 때까지 바텐더 생활을 계속하면서 짬짬이 주식 관련 서적을 10권 이상 읽었다.
    # TRANSLIT: gwi.ha.neun ja.geum.i 2.cheon.man weon.i doel ddae.gga.ji ba.ten.deo saeng.hwal.eul gye.sog.ha.myeon.seo jjam.jjam.i ju.sig gwan.ryeon seo.jeog.eul 10.gweon i.sang irg.eoss.da
    # ENGLISH: You continued your bartender life until your funds reached 20 million won, reading more than 10 books on stocks in your spare time.
    # CONFLICT: N1:자금이(nsubj), N2:원이(nsubj) under pred:'될 .doel' → default: N1(자금이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0042-s319': [('deprel', 2, 'nsubj:outer')],

    # MH2_0043-s157 [train]
    # TEXT: 기업이 본래의 업무가 아닌 재 (財) 테크에 혈안이 된 것은 큰 문제라 할 수 있다.
    # TRANSLIT: gi.eob.i bon.rae.yi eob.mu.ga a.nin jae ( cái ) te.keu.e hyeol.an.i doen geos.eun keun mun.je.ra hal su iss.da
    # ENGLISH: It can be said to be a serious problem that companies have become obsessed with financial speculation rather than their original business.
    # CONFLICT: N1:기업이(nsubj), N2:혈안이(nsubj) under pred:'된 .doen' → default: N1(기업이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0043-s157': [('deprel', 1, 'nsubj:outer')],

    # MH2_0043-s204 [train]
    # TEXT: 사회 간접 자본 투자 (특히 대도시) 의 대다수가 용지 비용이 큰 부분을 차지하는 점을 감안할 때, 지가가 높은 수준일수록 추진이 어렵게 된다.
    # TRANSLIT: sa.hoe gan.jeob ja.bon tu.ja ( teug.hi dae.do.si ) yi dae.da.su.ga yong.ji bi.yong.i keun bu.bun.eul cha.ji.ha.neun jeom.eul gam.an.hal ddae , ji.ga.ga nop.eun su.jun.il.su.rog chu.jin.i eo.ryeob.ge doen.da
    # ENGLISH: Considering that the majority of social overhead capital investment (especially in large cities) accounts for a large portion of land costs, the higher the land price, the harder it becomes to promote.
    # CONFLICT: N1:대다수가(nsubj), N2:비용이(nsubj) under pred:'차지하는 .cha.ji.ha.neun' → default: N1(대다수가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0043-s204': [('deprel', 10, 'nsubj:outer')],

    # MH2_0043-s213 [train]
    # TEXT: 그러나 '토지' 라는 생활에 필수적인 재화가 투기의 대상이 되는 사태는 어떻게 하든지 예방하지 않으면 안된다.
    # TRANSLIT: geu.reo.na ' to.ji ' ra.neun saeng.hwal.e pil.su.jeog.in jae.hwa.ga tu.gi.yi dae.sang.i doe.neun sa.tae.neun eo.ddeoh.ge ha.deun.ji ye.bang.ha.ji anh.eu.myeon an.doen.da
    # ENGLISH: However, the situation in which "land", an essential good for daily life, becomes an object of speculation must be prevented by any means.
    # CONFLICT: N1:재화가(nsubj), N2:대상이(nsubj) under pred:'되는 .doe.neun' → default: N1(재화가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0043-s213': [('deprel', 8, 'nsubj:outer')],

    # MH2_0043-s220 [train]
    # TEXT: 일본의 경우 토지가 투기 대상이 된 가장 큰 이유는 세제 (稅制) 의 왜곡이다.
    # TRANSLIT: il.bon.yi gyeong.u to.ji.ga tu.gi dae.sang.i doen ga.jang keun i.yu.neun se.je ( shuìzhì ) yi wae.gog.i.da
    # ENGLISH: In the case of Japan, the biggest reason why land became an object of speculation is the distortion of the tax system.
    # CONFLICT: N1:토지가(nsubj), N2:대상이(nsubj) under pred:'된 .doen' → default: N1(토지가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0043-s220': [('deprel', 3, 'nsubj:outer')],

    # MH2_0043-s317 [train]
    # TEXT: '실적 장세' 가 상품 (주식) 의 종류에 따라 차이가 나는데 비해, '금융 상세' 는 상품 종류에 관계없이 일률적인 것이 특징이다.
    # TRANSLIT: ' sil.jeog jang.se ' ga sang.pum ( ju.sig ) yi jong.ryu.e dda.ra cha.i.ga na.neun.de bi.hae , ' geum.yung sang.se ' neun sang.pum jong.ryu.e gwan.gye.eobs.i il.ryul.jeog.in geos.i teug.jing.i.da
    # ENGLISH: While an "earnings-driven market" differs depending on the type of product (stock), the characteristic of a "financial-driven market" is that it is uniform regardless of product type.
    # CONFLICT: N1:장세(nsubj), N2:차이가(nsubj) under pred:'나는데 .na.neun.de' → default: N1(장세)→nsubj:outer [NEEDS REVIEW]
    'MH2_0043-s317': [('deprel', 3, 'nsubj:outer')],

    # MH2_0043-s381 [train]
    # TEXT: 그러나 실제로 버블이 문제가 되는 것은, 다음 시기의 가격이 불확실한 주식과 같은 자산이 있기 때문이다.
    # TRANSLIT: geu.reo.na sil.je.ro beo.beul.i mun.je.ga doe.neun geos.eun , da.eum si.gi.yi ga.gyeog.i bul.hwag.sil.han ju.sig.gwa gat.eun ja.san.i iss.gi ddae.mun.i.da
    # ENGLISH: However, the reason why bubbles actually become a problem is that there are assets such as stocks whose future prices are uncertain.
    # CONFLICT: N1:버블이(nsubj), N2:문제가(nsubj) under pred:'되는 .doe.neun' → default: N1(버블이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0043-s381': [('deprel', 3, 'nsubj:outer')],

    # MH2_0043-s418 [train]
    # TEXT: 이것은 실제의 자산 가격이 기본 가격이 아닌, 다시 말하면 버블이 포함되어 있는 것을 나타낸다.
    # TRANSLIT: i.geos.eun sil.je.yi ja.san ga.gyeog.i gi.bon ga.gyeog.i a.nin , da.si mal.ha.myeon beo.beul.i po.ham.doe.eo iss.neun geos.eul na.ta.naen.da
    # ENGLISH: This indicates that the actual asset price is not the fundamental price — in other words, it contains a bubble.
    # CONFLICT: N1:가격이(nsubj), N2:가격이(nsubj) under pred:'아닌 .a.nin' → default: N1(가격이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0043-s418': [('deprel', 4, 'nsubj:outer')],

    # MH2_0043-s427 [train]
    # TEXT: 또한 국토가 좁은 네덜란드의 경우, 토지가 투기 대상이 된 것은 놀라운 사실이 아니다.
    # TRANSLIT: ddo.han gug.to.ga job.eun ne.deol.ran.deu.yi gyeong.u , to.ji.ga tu.gi dae.sang.i doen geos.eun nol.ra.un sa.sil.i a.ni.da
    # ENGLISH: Also, in the case of the Netherlands, a country with small territory, it is not a surprising fact that land became an object of speculation.
    # CONFLICT: N1:토지가(nsubj), N2:대상이(nsubj) under pred:'된 .doen' → default: N1(토지가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0043-s427': [('deprel', 7, 'nsubj:outer')],

    # MH2_0043-s432 [train]
    # TEXT: 가격이 상승함에 따라 튤립 재배와 무관한 사람들까지 투기에 참가하여 많은 사람들이 갑자기 부자가 되었다.
    # TRANSLIT: ga.gyeog.i sang.seung.ham.e dda.ra tyul.rib jae.bae.wa mu.gwan.han sa.ram.deul.gga.ji tu.gi.e cham.ga.ha.yeo manh.eun sa.ram.deul.i gab.ja.gi bu.ja.ga doe.eoss.da
    # ENGLISH: As prices rose, even people unrelated to tulip cultivation participated in speculation, and many people suddenly became rich.
    # CONFLICT: N1:사람들이(nsubj), N2:부자가(nsubj) under pred:'되었다 .doe.eoss.da' → default: N1(사람들이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0043-s432': [('deprel', 11, 'nsubj:outer')],

    # MH2_0043-s47 [train]
    # TEXT: 가격이 상승하는 것이 문제가 아니라 그로부터 발생한 이익을 다수가 누리지 못하는 것이 문제라는 식의 의견도 제시되었다.
    # TRANSLIT: ga.gyeog.i sang.seung.ha.neun geos.i mun.je.ga a.ni.ra geu.ro.bu.teo bal.saeng.han i.ig.eul da.su.ga nu.ri.ji mos.ha.neun geos.i mun.je.ra.neun sig.yi yi.gyeon.do je.si.doe.eoss.da
    # ENGLISH: Opinions were also presented that the problem is not that prices rise, but that the majority cannot enjoy the profits generated from it.
    # CONFLICT: N1:것이(nsubj), N2:문제가(nsubj) under pred:'아니라 .a.ni.ra' → default: N1(것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0043-s47': [('deprel', 3, 'nsubj:outer')],

    # MH2_0043-s53 [train]
    # TEXT: 사실 이때에는 정통 경제학 이론도 자산 가격의 상승이 경제 성장을 촉진할 가능성이 있다고 인식하였다.
    # TRANSLIT: sa.sil i.ddae.e.neun jeong.tong gyeong.je.hag i.ron.do ja.san ga.gyeog.yi sang.seung.i gyeong.je seong.jang.eul chog.jin.hal ga.neung.seong.i iss.da.go in.sig.ha.yeoss.da
    # ENGLISH: In fact, at that time, orthodox economic theory also recognized that rising asset prices had the potential to stimulate economic growth.
    # CONFLICT: N1:상승이(nsubj), N2:가능성이(nsubj) under pred:'있다고 .iss.da.go' → default: N1(상승이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0043-s53': [('deprel', 8, 'nsubj:outer')],

    # MH2_0043-s60 [train]
    # TEXT: 이러한 사실과 자산 가격 동향을 연결하면 확실히 자산 가격 상승이 경기 확대의 요인이 되었던 것으로 보인다.
    # TRANSLIT: i.reo.han sa.sil.gwa ja.san ga.gyeog dong.hyang.eul yeon.gyeol.ha.myeon hwag.sil.hi ja.san ga.gyeog sang.seung.i gyeong.gi hwag.dae.yi yo.in.i doe.eoss.deon geos.eu.ro bo.in.da
    # ENGLISH: Connecting this fact with asset price trends, it certainly appears that rising asset prices were a factor in economic expansion.
    # CONFLICT: N1:상승이(nsubj), N2:요인이(nsubj) under pred:'되었던 .doe.eoss.deon' → default: N1(상승이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0043-s60': [('deprel', 10, 'nsubj:outer')],

    # MH2_0045-s315 [train]
    # TEXT: 뻬레스트로이카의 좌초에 대해 상황이 엉망이 되면서 많은 사람들이 고르비에게 책임을 돌려 비난하기 시작했다.
    # TRANSLIT: bbe.re.seu.teu.ro.i.ka.yi jwa.cho.e dae.hae sang.hwang.i eong.mang.i doe.myeon.seo manh.eun sa.ram.deul.i go.reu.bi.e.ge chaeg.im.eul dol.ryeo bi.nan.ha.gi si.jag.haess.da
    # ENGLISH: As the situation became chaotic with the failure of perestroika, many people began to blame Gorbi and criticize him.
    # CONFLICT: N1:상황이(nsubj), N2:엉망이(nsubj) under pred:'되면서 .doe.myeon.seo' → default: N1(상황이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0045-s315': [('deprel', 4, 'nsubj:outer')],

    # MH2_0045-s344 [train]
    # TEXT: 뿌치와 관련한 고르비의 비극은 그가 관료주의적 모리배들과 어울려 더이상 이 같은 참신한 민주세력의 기수가 되지 못했음에 있었다.
    # TRANSLIT: bbu.chi.wa gwan.ryeon.han go.reu.bi.yi bi.geug.eun geu.ga gwan.ryo.ju.yi.jeog mo.ri.bae.deul.gwa eo.ul.ryeo deo.i.sang i gat.eun cham.sin.han min.ju.se.ryeog.yi gi.su.ga doe.ji mos.haess.eum.e iss.eoss.da
    # ENGLISH: Gorbi's tragedy in relation to the coup was that by associating with bureaucratic opportunists, he was no longer able to be the standard-bearer of such fresh democratic forces.
    # CONFLICT: N1:그가(nsubj), N2:기수가(nsubj) under pred:'되지 .doe.ji' → default: N1(그가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0045-s344': [('deprel', 5, 'nsubj:outer')],

    # MH2_0045-s488 [train]
    # TEXT: 그러나 이들 서민들은 이들 상점이 값이 싼 대신 비할 수 없는 대가를 치르고 있다.
    # TRANSLIT: geu.reo.na i.deul seo.min.deul.eun i.deul sang.jeom.i gabs.i ssan dae.sin bi.hal su eobs.neun dae.ga.reul chi.reu.go iss.da
    # ENGLISH: However, these ordinary people are paying an incomparable price for these stores being cheap.
    # CONFLICT: N1:상점이(nsubj), N2:값이(nsubj) under pred:'싼 .ssan' → default: N1(상점이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0045-s488': [('deprel', 5, 'nsubj:outer')],

    # MH2_0045-s50 [train]
    # TEXT: 경제가 엉망이 되면서 시민들은 무력감에 빠져 들었고 고르바초프의 호소가 공허해지면서 사회는 무정부상태에 빠쳐 들어갔다.
    # TRANSLIT: gyeong.je.ga eong.mang.i doe.myeon.seo si.min.deul.eun mu.ryeog.gam.e bba.jyeo deul.eoss.go go.reu.ba.cho.peu.yi ho.so.ga gong.heo.hae.ji.myeon.seo sa.hoe.neun mu.jeong.bu.sang.tae.e bba.chyeo deul.eo.gass.da
    # ENGLISH: As the economy fell into chaos, citizens fell into a sense of powerlessness, and as Gorbachev's appeals became hollow, society fell into anarchy.
    # CONFLICT: N1:경제가(nsubj), N2:엉망이(nsubj) under pred:'되면서 .doe.myeon.seo' → default: N1(경제가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0045-s50': [('deprel', 1, 'nsubj:outer')],

    # MH2_0045-s511 [train]
    # TEXT: 서울에서 온 한 상사의 젊은 직원이 바로 이 같은 마피아의 농간에 걸려 2만달러어치의 현금과 물품들을 몽땅 털린 일이 있다.
    # TRANSLIT: seo.ul.e.seo on han sang.sa.yi jeorm.eun jig.weon.i ba.ro i gat.eun ma.pi.a.yi nong.gan.e geol.ryeo 2.man.dal.reo.eo.chi.yi hyeon.geum.gwa mul.pum.deul.eul mong.ddang teol.rin il.i iss.da
    # ENGLISH: A young employee of a trading company from Seoul was caught in the machinations of just such a mafia and had all 20,000 dollars' worth of cash and goods stolen.
    # CONFLICT: N1:직원이(nsubj), N2:일이(nsubj) under pred:'있다 .iss.da' → default: N1(직원이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0045-s511': [('deprel', 6, 'nsubj:outer')],

    # MH2_0046-s11 [train]
    # TEXT: 물론 임화는 당대의 문학이념과 그의 소설론과의 관계를 상술하고 있지는 않으며 이 점이 그의 이론에 무이념적이고 비역사적이라는 혐의를 씌우는 요인이 되고 있다.
    # TRANSLIT: mul.ron im.hwa.neun dang.dae.yi mun.hag.i.nyeom.gwa geu.yi so.seol.ron.gwa.yi gwan.gye.reul sang.sul.ha.go iss.ji.neun anh.eu.myeo i jeom.i geu.yi i.ron.e mu.i.nyeom.jeog.i.go bi.yeog.sa.jeog.i.ra.neun hyeom.yi.reul ssyi.u.neun yo.in.i doe.go iss.da
    # ENGLISH: Of course, Im Hwa does not elaborate on the relationship between the literary ideology of the time and his theory of fiction, and this point is becoming a factor that casts suspicion on his theory as unideological and ahistorical.
    # CONFLICT: N1:점이(nsubj), N2:요인이(nsubj) under pred:'되고 .doe.go' → default: N1(점이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0046-s11': [('deprel', 12, 'nsubj:outer')],

    # MH2_0046-s227 [train]
    # TEXT: 김남천은 고발문학론, 모랄론, 도덕론, 장편소설개조론을 거치면서 서구에서의 로망의 붕괴와 관련하여 조선의 구체적 극복이 로망의 개조와 관련이 있음을 끊임없이 강조하여 왔다.
    # TRANSLIT: gim.nam.cheon.eun go.bal.mun.hag.ron , mo.ral.ron , do.deog.ron , jang.pyeon.so.seol.gae.jo.ron.eul geo.chi.myeon.seo seo.gu.e.seo.yi ro.mang.yi bung.goe.wa gwan.ryeon.ha.yeo jo.seon.yi gu.che.jeog geug.bog.i ro.mang.yi gae.jo.wa gwan.ryeon.i iss.eum.eul ggeunh.im.eobs.i gang.jo.ha.yeo wass.da
    # ENGLISH: Kim Nam-cheon, through his accusation literature theory, moral theory, ethics theory, and long-novel reform theory, continuously emphasized that Korea's concrete overcoming is related to the reform of the roman, in connection with the collapse of the roman in the West.
    # CONFLICT: N1:극복이(nsubj), N2:관련이(nsubj) under pred:'있음을 .iss.eum.eul' → default: N1(극복이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0046-s227': [('deprel', 16, 'nsubj:outer')],

    # MH2_0046-s264 [train]
    # TEXT: 이렇게 보면 고발문학론이 왜 리얼리즘이 되는지 대강의 의미는 짐작할 수 있다.
    # TRANSLIT: i.reoh.ge bo.myeon go.bal.mun.hag.ron.i wae ri.eol.ri.jeum.i doe.neun.ji dae.gang.yi yi.mi.neun jim.jag.hal su iss.da
    # ENGLISH: Seen this way, we can get a general idea of why accusation literature theory becomes realism.
    # CONFLICT: N1:고발문학론이(nsubj), N2:리얼리즘이(nsubj) under pred:'되는지 .doe.neun.ji' → default: N1(고발문학론이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0046-s264': [('deprel', 3, 'nsubj:outer')],

    # MH2_0046-s277 [train]
    # TEXT: 따라서 현실성이 부여되기 위해서는 작가가 주인공처럼 현실에서 체험하는 부분을 형상화할 필요성이 있고, 이것이 바로 소시민 지식인 번뇌, 즉 자기고발이 된다.
    # TRANSLIT: dda.ra.seo hyeon.sil.seong.i bu.yeo.doe.gi wi.hae.seo.neun jag.ga.ga ju.in.gong.cheo.reom hyeon.sil.e.seo che.heom.ha.neun bu.bun.eul hyeong.sang.hwa.hal pil.yo.seong.i iss.go , i.geos.i ba.ro so.si.min ji.sig.in beon.noe , jeug ja.gi.go.bal.i doen.da
    # ENGLISH: Therefore, in order for reality to be conferred, the author needs to give form to the parts experienced in reality like the protagonist, and this precisely becomes the anxiety of petty-bourgeois intellectuals — i.e., self-accusation.
    # CONFLICT: N1:이것이(nsubj), N2:번뇌(nsubj) under pred:'된다 .doen.da' → default: N1(이것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0046-s277': [('deprel', 14, 'nsubj:outer')],

    # MH2_0046-s279 [train]
    # TEXT: 오히려 이러한 점은 어디까지나 전형이 리얼리즘의 핵심적 범주이며 그것이 상황 속에서 인물이 형성된다고 하는 일반론적 원칙의 강조라고 보여진다.
    # TRANSLIT: o.hi.ryeo i.reo.han jeom.eun eo.di.gga.ji.na jeon.hyeong.i ri.eol.ri.jeum.yi haeg.sim.jeog beom.ju.i.myeo geu.geos.i sang.hwang sog.e.seo in.mul.i hyeong.seong.doen.da.go ha.neun il.ban.ron.jeog weon.chig.yi gang.jo.ra.go bo.yeo.jin.da
    # ENGLISH: Rather, this point seems to be an emphasis on the general principle that the typical is the core category of realism and that characters are formed within situations.
    # CONFLICT: N1:그것이(nsubj), N2:인물이(nsubj) under pred:'형성된다고 .hyeong.seong.doen.da.go' → default: N1(그것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0046-s279': [('deprel', 9, 'nsubj:outer')],

    # MH2_0046-s303 [train]
    # TEXT: 이런 과정에는 반드시 그것을 자기 것으로 형상화하는 주체화가 수반되는데, 이 주체화의 과정이 바로 모랄이 된다.
    # TRANSLIT: i.reon gwa.jeong.e.neun ban.deu.si geu.geos.eul ja.gi geos.eu.ro hyeong.sang.hwa.ha.neun ju.che.hwa.ga su.ban.doe.neun.de , i ju.che.hwa.yi gwa.jeong.i ba.ro mo.ral.i doen.da
    # ENGLISH: This process is necessarily accompanied by subjectification that gives form to it as one's own, and this process of subjectification precisely becomes the "moral."
    # CONFLICT: N1:과정이(nsubj), N2:모랄이(nsubj) under pred:'된다 .doen.da' → default: N1(과정이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0046-s303': [('deprel', 13, 'nsubj:outer')],

    # MH2_0051-s17 [train]
    # TEXT: 지구가 우주의 중심이 아닌 것처럼 유럽 또한 세계의 중심이 아니었다.
    # TRANSLIT: ji.gu.ga u.ju.yi jung.sim.i a.nin geos.cheo.reom yu.reob ddo.han se.gye.yi jung.sim.i a.ni.eoss.da
    # ENGLISH: Just as the Earth is not the center of the universe, Europe was also not the center of the world.
    # CONFLICT: N1:지구가(nsubj), N2:중심이(csubj) under pred:'아닌 .a.nin' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0051-s17': [('deprel', 1, 'nsubj:outer')],

    # MH2_0051-s340 [train]
    # TEXT: 우리가 텔레비전에서 기아에 희생된 소말리아 어린이들이나 포탄을 맞은 사라예보의 여자들과 어린이들을 보면서 가슴이 찡 해지는 것이 바로 그 같은 경우다.
    # TRANSLIT: u.ri.ga tel.re.bi.jeon.e.seo gi.a.e hyi.saeng.doen so.mal.ri.a eo.rin.i.deul.i.na po.tan.eul maj.eun sa.ra.ye.bo.yi yeo.ja.deul.gwa eo.rin.i.deul.eul bo.myeon.seo ga.seum.i jjing hae.ji.neun geos.i ba.ro geu gat.eun gyeong.u.da
    # ENGLISH: What we see on television — children in Somalia who are victims of famine or women and children in Sarajevo who have been hit by shells — moving us to tears is precisely such a case.
    # CONFLICT: N1:우리가(nsubj), N2:가슴이(nsubj) under pred:'해지는 .hae.ji.neun' → default: N1(우리가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0051-s340': [('deprel', 1, 'nsubj:outer')],

    # MH2_0062-s114 [train]
    # TEXT: 그럼에도 스포츠 공시학에서 이러한 접근방식이 정치 커뮤니케이션에서어럼 같은 반향이 올 수 있을 것이냐 하는 것은 재검토되어야 한다.
    # TRANSLIT: geu.reom.e.do seu.po.cheu gong.si.hag.e.seo i.reo.han jeob.geun.bang.sig.i jeong.chi keo.myu.ni.ke.i.syeon.e.seo.eo.reom gat.eun ban.hyang.i ol su iss.eul geos.i.nya ha.neun geos.eun jae.geom.to.doe.eo.ya han.da
    # ENGLISH: Nevertheless, whether such an approach in sports semiotics can produce the same resonance as in political communication is something that needs to be re-examined.
    # CONFLICT: N1:접근방식이(nsubj), N2:반향이(nsubj) under pred:'올 .ol' → default: N1(접근방식이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0062-s114': [('deprel', 5, 'nsubj:outer')],

    # MH2_0062-s137 [train]
    # TEXT: 패러다임 변환을 통하여 이미 지적하였듯이 연구를 끌어내는 문제제기가 정반대적인 것이 되었다.
    # TRANSLIT: pae.reo.da.im byeon.hwan.eul tong.ha.yeo i.mi ji.jeog.ha.yeoss.deus.i yeon.gu.reul ggeul.eo.nae.neun mun.je.je.gi.ga jeong.ban.dae.jeog.in geos.i doe.eoss.da
    # ENGLISH: As already noted through the paradigm shift, the problematization that drives research has become the complete opposite.
    # CONFLICT: N1:문제제기가(nsubj), N2:것이(nsubj) under pred:'되었다 .doe.eoss.da' → default: N1(문제제기가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0062-s137': [('deprel', 8, 'nsubj:outer')],

    # MH2_0062-s139 [train]
    # TEXT: 더욱 정확히 논하여, 누가, 어떤 내용을, 왜, 그리고 어떠한 이용을 위하여 선택하는가가 중요한 연구주제가 된 것이다.
    # TRANSLIT: deo.ug jeong.hwag.hi non.ha.yeo , nu.ga , eo.ddeon nae.yong.eul , wae , geu.ri.go eo.ddeo.han i.yong.eul wi.ha.yeo seon.taeg.ha.neun.ga.ga jung.yo.han yeon.gu.ju.je.ga doen geos.i.da
    # ENGLISH: To put it more precisely, who selects what content, why, and for what use has become an important research topic.
    # CONFLICT: N1:위하여(nsubj), N2:연구주제가(nsubj) under pred:'된 .doen' → default: N1(위하여)→nsubj:outer [NEEDS REVIEW]
    'MH2_0062-s139': [('deprel', 15, 'nsubj:outer')],

    # MH2_0062-s147 [train]
    # TEXT: 일간신문지의 스ㅍ으란 기사를 읽는 시간, 텔레비전에 의한 스포츠 중계방송의 이용, 미디어에 따른 특정한 스포츠 종류에 대한 관심이 연구의 대상이 될 수 있다.
    # TRANSLIT: il.gan.sin.mun.ji.yi seuㅍ.eu.ran gi.sa.reul irg.neun si.gan , tel.re.bi.jeon.e yi.han seu.po.cheu jung.gye.bang.song.yi i.yong , mi.di.eo.e dda.reun teug.jeong.han seu.po.cheu jong.ryu.e dae.han gwan.sim.i yeon.gu.yi dae.sang.i doel su iss.da
    # ENGLISH: The time spent reading sports articles in daily newspapers, the use of sports broadcasting by television, and interest in specific types of sports by medium can be subjects of study.
    # CONFLICT: N1:관심이(nsubj), N2:대상이(nsubj) under pred:'될 .doel' → default: N1(관심이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0062-s147': [('deprel', 19, 'nsubj:outer')],

    # MH2_0062-s174 [train]
    # TEXT: 예를 들어 반응의 각도, 스포츠 경기가 개최되는 장소, 관람자들이 관전하는 장소의 안락성, 그리고 개인의 개별적인 선경험 등이 변인이 되고 있다.
    # TRANSLIT: ye.reul deul.eo ban.eung.yi gag.do , seu.po.cheu gyeong.gi.ga gae.choe.doe.neun jang.so , gwan.ram.ja.deul.i gwan.jeon.ha.neun jang.so.yi an.rag.seong , geu.ri.go gae.in.yi gae.byeol.jeog.in seon.gyeong.heom deung.i byeon.in.i doe.go iss.da
    # ENGLISH: For example, the angle of response, the venue where sports events are held, the comfort of the places where spectators watch, and individual prior experiences, etc., are becoming variables.
    # CONFLICT: N1:등이(nsubj), N2:변인이(nsubj) under pred:'되고 .doe.go' → default: N1(등이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0062-s174': [('deprel', 20, 'nsubj:outer')],

    # MH2_0062-s314 [train]
    # TEXT: 1968년 멕시코대회에서 미국에만 적용되는 중계허가권료가 450만달러가 되었다.
    # TRANSLIT: 1968.nyeon meg.si.ko.dae.hoe.e.seo mi.gug.e.man jeog.yong.doe.neun jung.gye.heo.ga.gweon.ryo.ga 450.man.dal.reo.ga doe.eoss.da
    # ENGLISH: At the 1968 Mexico Games, the broadcasting rights fee applied only to the United States became 4.5 million dollars.
    # CONFLICT: N1:중계허가권료가(nsubj), N2:450만달러가(csubj) under pred:'되었다 .doe.eoss.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0062-s314': [('deprel', 5, 'nsubj:outer')],

    # MH2_0062-s38 [train]
    # TEXT: 스포츠경기장 주위를 둘러싼 벽면광고, 운동선수들이 유니폼에 실려 있는 특정회사의 신체광고는 커뮤니케이션 행위로서 스포츠가 중요한 기업정책의 일부분이 되도록 하고 있다.
    # TRANSLIT: seu.po.cheu.gyeong.gi.jang ju.wi.reul dul.reo.ssan byeog.myeon.gwang.go , un.dong.seon.su.deul.i yu.ni.pom.e sil.ryeo iss.neun teug.jeong.hoe.sa.yi sin.che.gwang.go.neun keo.myu.ni.ke.i.syeon haeng.wi.ro.seo seu.po.cheu.ga jung.yo.han gi.eob.jeong.chaeg.yi il.bu.bun.i doe.do.rog ha.go iss.da
    # ENGLISH: Wall advertisements surrounding sports venues and corporate body advertising on athletes' uniforms are making sports as a communication act an important part of corporate policy.
    # CONFLICT: N1:스포츠가(nsubj), N2:일부분이(nsubj) under pred:'되도록 .doe.do.rog' → default: N1(스포츠가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0062-s38': [('deprel', 14, 'nsubj:outer')],

    # MH2_0062-s39 [train]
    # TEXT: 가수나 인기연예인이 주가 되었던 광고모델로 인기 운동선수들이 등장하고 있음은 바로 스포츠와 미디어에 의해 창출된 변화된 쇼스포츠의 단면을 보여주고 있다.
    # TRANSLIT: ga.su.na in.gi.yeon.ye.in.i ju.ga doe.eoss.deon gwang.go.mo.del.ro in.gi un.dong.seon.su.deul.i deung.jang.ha.go iss.eum.eun ba.ro seu.po.cheu.wa mi.di.eo.e yi.hae chang.chul.doen byeon.hwa.doen syo.seu.po.cheu.yi dan.myeon.eul bo.yeo.ju.go iss.da
    # ENGLISH: The appearance of popular athletes as advertising models, which had been dominated by singers and popular entertainers, is showing a cross-section of changed show sports created by sports and media.
    # CONFLICT: N1:가수나(nsubj), N2:주가(nsubj) under pred:'되었던 .doe.eoss.deon' → default: N1(가수나)→nsubj:outer [NEEDS REVIEW]
    'MH2_0062-s39': [('deprel', 1, 'nsubj:outer')],

    # MH2_0062-s418 [train]
    # TEXT: 모든 스포츠 유형은 그것이 인기가 있든 없든, 올림픽 경기의 쇼적 성격을 규명하는 본질이 되고 있다.
    # TRANSLIT: mo.deun seu.po.cheu yu.hyeong.eun geu.geos.i in.gi.ga iss.deun eobs.deun , ol.rim.pig gyeong.gi.yi syo.jeog seong.gyeog.eul gyu.myeong.ha.neun bon.jil.i doe.go iss.da
    # ENGLISH: All types of sports, whether popular or not, are becoming the essence that defines the show character of the Olympic Games.
    # CONFLICT: N1:그것이(nsubj), N2:인기가(nsubj) under pred:'있든 .iss.deun' → default: N1(그것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0062-s418': [('deprel', 4, 'nsubj:outer')],

    # MH2_0062-s425 [train]
    # TEXT: 직업 스포츠는 항시 고능률 스포츠이지만, 역으로 고능률 스포츠가 항시 직업 스포츠가 되는 것은 아니다.
    # TRANSLIT: jig.eob seu.po.cheu.neun hang.si go.neung.ryul seu.po.cheu.i.ji.man , yeog.eu.ro go.neung.ryul seu.po.cheu.ga hang.si jig.eob seu.po.cheu.ga doe.neun geos.eun a.ni.da
    # ENGLISH: Professional sports is always high-performance sports, but conversely, high-performance sports does not always become professional sports.
    # CONFLICT: N1:스포츠가(nsubj), N2:스포츠가(csubj) under pred:'되는 .doe.neun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0062-s425': [('deprel', 9, 'nsubj:outer')],

    # MH2_0062-s80 [train]
    # TEXT: 그 범위가 넓어지고 확대된 산업화는 매스미디어가 강력할 뿐만 아니라 거의 전지전능한 선동자, 교시자가 된다는 대중사회를 걱극 견지하는 틀이 되었다.
    # TRANSLIT: geu beom.wi.ga neorb.eo.ji.go hwag.dae.doen san.eob.hwa.neun mae.seu.mi.di.eo.ga gang.ryeog.hal bbun.man a.ni.ra geo.yi jeon.ji.jeon.neung.han seon.dong.ja , gyo.si.ja.ga doen.da.neun dae.jung.sa.hoe.reul geog.geug gyeon.ji.ha.neun teul.i doe.eoss.da
    # ENGLISH: The industrialization that has widened and expanded its scope became a framework that actively maintains a mass society where mass media is not only powerful but becomes an almost omnipotent agitator and instructor.
    # CONFLICT: N1:매스미디어가(nsubj), N2:선동자(csubj) under pred:'된다는 .doen.da.neun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0062-s80': [('deprel', 6, 'nsubj:outer')],

    # MH2_0066-s296 [train]
    # TEXT: 본래 시는 말을 개념지시에 입각해 쓴 쪽이기보다 함축적 의미가 배가 되도록 사용해야 한다.
    # TRANSLIT: bon.rae si.neun mal.eul gae.nyeom.ji.si.e ib.gag.hae sseun jjog.i.gi.bo.da ham.chug.jeog yi.mi.ga bae.ga doe.do.rog sa.yong.hae.ya han.da
    # ENGLISH: Poetry should fundamentally be used so that connotative meanings are doubled, rather than being written based on conceptual reference.
    # CONFLICT: N1:의미가(nsubj), N2:배가(nsubj) under pred:'되도록 .doe.do.rog' → default: N1(의미가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0066-s296': [('deprel', 9, 'nsubj:outer')],

    # MH2_0066-s319 [train]
    # TEXT: 그것이 시가 되기 위해서는 적어도 사상 관념의 감각적 실체화가 이루어져야 한다.
    # TRANSLIT: geu.geos.i si.ga doe.gi wi.hae.seo.neun jeog.eo.do sa.sang gwan.nyeom.yi gam.gag.jeog sil.che.hwa.ga i.ru.eo.jyeo.ya han.da
    # ENGLISH: In order for it to become a poem, at least the sensory embodiment of ideas and concepts must be achieved.
    # CONFLICT: N1:그것이(nsubj), N2:시가(nsubj) under pred:'되기 .doe.gi' → default: N1(그것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0066-s319': [('deprel', 1, 'nsubj:outer')],

    # MH2_0066-s339 [train]
    # TEXT: 거듭 되풀이 되지만 만해는 일체의 민족운동이 가차없이 처단 금제가 된 일제 식민지 시대를 살았다.
    # TRANSLIT: geo.deub doe.pul.i doe.ji.man man.hae.neun il.che.yi min.jog.un.dong.i ga.cha.eobs.i cheo.dan geum.je.ga doen il.je sig.min.ji si.dae.reul sal.ass.da
    # ENGLISH: It will be repeated — Manhae lived through the Japanese colonial era when all national movements were ruthlessly suppressed and prohibited.
    # CONFLICT: N1:민족운동이(nsubj), N2:금제가(nsubj) under pred:'된 .doen' → default: N1(민족운동이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0066-s339': [('deprel', 6, 'nsubj:outer')],

    # MH2_0066-s354 [train]
    # TEXT: 그럼에도 불구하고 그는 일제의 매질이 빌미가 된 병으로 죽지도 않았고, 부당한 규제, 간섭을 받은 나머지 울분에 쌓여 죽지도 않았다.
    # TRANSLIT: geu.reom.e.do bul.gu.ha.go geu.neun il.je.yi mae.jil.i bil.mi.ga doen byeong.eu.ro jug.ji.do anh.ass.go , bu.dang.han gyu.je , gan.seob.eul bad.eun na.meo.ji ul.bun.e ssah.yeo jug.ji.do anh.ass.da
    # ENGLISH: Nevertheless, he did not die from illness caused by Japanese beatings, nor did he die full of resentment from unjust regulations and interference.
    # CONFLICT: N1:매질이(nsubj), N2:빌미가(nsubj) under pred:'된 .doen' → default: N1(매질이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0066-s354': [('deprel', 5, 'nsubj:outer')],

    # MH2_0066-s382 [train]
    # TEXT: 다른 또 하나의 변별적인 특징은 그들이 한학, 경서에 깊이 침윤된 사림계층 출신이 아니라 중인들이거나 오랫동안 보수사림과는 무관한 생활을 해온 집안 출신이라는 점이다.
    # TRANSLIT: da.reun ddo ha.na.yi byeon.byeol.jeog.in teug.jing.eun geu.deul.i han.hag , gyeong.seo.e gip.i chim.yun.doen sa.rim.gye.cheung chul.sin.i a.ni.ra jung.in.deul.i.geo.na o.raes.dong.an bo.su.sa.rim.gwa.neun mu.gwan.han saeng.hwal.eul hae.on jib.an chul.sin.i.ra.neun jeom.i.da
    # ENGLISH: Another distinguishing characteristic is that they are not from the sarim class deeply steeped in Chinese studies and Confucian classics, but from the middle class or from families long unrelated to conservative Confucian scholars.
    # CONFLICT: N1:그들이(nsubj), N2:출신이(nsubj) under pred:'아니라 .a.ni.ra' → default: N1(그들이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0066-s382': [('deprel', 6, 'nsubj:outer')],

    # MH2_0066-s42 [train]
    # TEXT: 이 책에서 만해는 불교가 사람의 큰 슬기, 큰 마음을 일깨워 미망에서 헤어나게 하는데 그 궁극의 목표가 있다고 설파했다.
    # TRANSLIT: i chaeg.e.seo man.hae.neun bul.gyo.ga sa.ram.yi keun seul.gi , keun ma.eum.eul il.ggae.weo mi.mang.e.seo he.eo.na.ge ha.neun.de geu gung.geug.yi mog.pyo.ga iss.da.go seol.pa.haess.da
    # ENGLISH: In this book, Manhae preached that Buddhism has its ultimate goal in awakening people's great wisdom and great minds to escape from delusion.
    # CONFLICT: N1:불교가(nsubj), N2:목표가(nsubj) under pred:'있다고 .iss.da.go' → default: N1(불교가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0066-s42': [('deprel', 4, 'nsubj:outer')],

    # MH2_0066-s442 [train]
    # TEXT: 그의 수학이력을 뒤져보면 무애가 향리에서 한문을 읽다가 평야고보에 입학한 것이 열세살 살였다.
    # TRANSLIT: geu.yi su.hag.i.ryeog.eul dwi.jyeo.bo.myeon mu.ae.ga hyang.ri.e.seo han.mun.eul irg.da.ga pyeong.ya.go.bo.e ib.hag.han geos.i yeol.se.sal sal.yeoss.da
    # ENGLISH: Looking into his academic history, we find that Muae entered Pyeongya Middle School at age thirteen after reading Chinese texts in his hometown.
    # CONFLICT: N1:무애가(nsubj), N2:것이(nsubj) under pred:'살였다 .sal.yeoss.da' → default: N1(무애가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0066-s442': [('deprel', 4, 'nsubj:outer')],

    # MH2_0066-s497 [train]
    # TEXT: 우선 무애 자신이 동인운동을 튼튼하게 지탱해 나갈 정도로 부유한 집안의 출신이 아니었다.
    # TRANSLIT: u.seon mu.ae ja.sin.i dong.in.un.dong.eul teun.teun.ha.ge ji.taeng.hae na.gal jeong.do.ro bu.yu.han jib.an.yi chul.sin.i a.ni.eoss.da
    # ENGLISH: First of all, Muae himself was not from a wealthy enough family to solidly sustain the Dongin movement.
    # CONFLICT: N1:자신이(nsubj), N2:출신이(nsubj) under pred:'아니었다 .a.ni.eoss.da' → default: N1(자신이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0066-s497': [('deprel', 3, 'nsubj:outer')],

    # MH2_0066-s502 [train]
    # TEXT: 금성이 그 기획 때부터 무애가 주동이 된 사실은 여러 가지 사실로 입증된다.
    # TRANSLIT: geum.seong.i geu gi.hoeg ddae.bu.teo mu.ae.ga ju.dong.i doen sa.sil.eun yeo.reo ga.ji sa.sil.ro ib.jeung.doen.da
    # ENGLISH: The fact that Muae was the driving force behind Geumsong from its planning stage is proven by various facts.
    # CONFLICT: N1:금성이(nsubj), N2:무애가(nsubj), N3:주동이(nsubj) under pred:'된 .doen' → 3-way default: N1,N2→nsubj:outer [NEEDS REVIEW]
    'MH2_0066-s502': [('deprel', 1, 'nsubj:outer'), ('deprel', 5, 'nsubj:outer')],

    # MH2_0066-s669 [train]
    # TEXT: 그리하여 근대 이후 시들이 정형률을 등지고 자유기가 된 것이다.
    # TRANSLIT: geu.ri.ha.yeo geun.dae i.hu si.deul.i jeong.hyeong.ryul.eul deung.ji.go ja.yu.gi.ga doen geos.i.da
    # ENGLISH: Thus, after modern times, poems turned away from fixed meter and became free verse.
    # CONFLICT: N1:시들이(nsubj), N2:자유기가(nsubj) under pred:'된 .doen' → default: N1(시들이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0066-s669': [('deprel', 4, 'nsubj:outer')],

    # MH2_0066-s679 [train]
    # TEXT: 그리고 그 성과는 무애 스스로가 小의 업적이 반휴지가 되었다고 단언했을 정도의 것이었다.
    # TRANSLIT: geu.ri.go geu seong.gwa.neun mu.ae seu.seu.ro.ga xiǎo.yi eob.jeog.i ban.hyu.ji.ga doe.eoss.da.go dan.eon.haess.eul jeong.do.yi geos.i.eoss.da
    # ENGLISH: And the results were such that Muae himself asserted that his own achievement had reached a half-resting point.
    # CONFLICT: N1:업적이(nsubj), N2:반휴지가(nsubj) under pred:'되었다고 .doe.eoss.da.go' → default: N1(업적이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0066-s679': [('deprel', 7, 'nsubj:outer')],

    # MH2_0068-s116 [train]
    # TEXT: 물론 권위 공간이 없다 하여 일본 주부가 권위가 없다는 것은 아니다.
    # TRANSLIT: mul.ron gweon.wi gong.gan.i eobs.da ha.yeo il.bon ju.bu.ga gweon.wi.ga eobs.da.neun geos.eun a.ni.da
    # ENGLISH: Of course, saying that there is no space of authority does not mean that Japanese housewives have no authority.
    # CONFLICT: N1:주부가(nsubj), N2:권위가(nsubj) under pred:'없다는 .eobs.da.neun' → default: N1(주부가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0068-s116': [('deprel', 7, 'nsubj:outer')],

    # MH2_0068-s163 [train]
    # TEXT: 이제 서구문화의 시련기를 지나 문화가 경쟁의 중요한 내용이 되는 시기에 한국과 일본은 세계문화에 크게 이바지할 것을 의심치 않는다.
    # TRANSLIT: i.je seo.gu.mun.hwa.yi si.ryeon.gi.reul ji.na mun.hwa.ga gyeong.jaeng.yi jung.yo.han nae.yong.i doe.neun si.gi.e han.gug.gwa il.bon.eun se.gye.mun.hwa.e keu.ge i.ba.ji.hal geos.eul yi.sim.chi anh.neun.da
    # ENGLISH: Now, having passed through the ordeal of Western culture and entering a period when culture becomes an important content of competition, I have no doubt that Korea and Japan will make great contributions to world culture.
    # CONFLICT: N1:문화가(nsubj), N2:내용이(csubj) under pred:'되는 .doe.neun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0068-s163': [('deprel', 5, 'nsubj:outer')],

    # MH2_0068-s173 [train]
    # TEXT: 그것을 보고 저는 이것이 다다미가 아니겠는가 하고 생각했습니다.
    # TRANSLIT: geu.geos.eul bo.go jeo.neun i.geos.i da.da.mi.ga a.ni.gess.neun.ga ha.go saeng.gag.haess.seub.ni.da
    # ENGLISH: Seeing that, I thought: could this not be tatami?
    # CONFLICT: N1:이것이(nsubj), N2:다다미가(csubj) under pred:'아니겠는가 .a.ni.gess.neun.ga' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0068-s173': [('deprel', 4, 'nsubj:outer')],

    # MH2_0068-s182 [train]
    # TEXT: 이것이 가장 큰 문제가 아닌가 생각합니다.
    # TRANSLIT: i.geos.i ga.jang keun mun.je.ga a.nin.ga saeng.gag.hab.ni.da
    # ENGLISH: I think this is the biggest problem.
    # CONFLICT: N1:이것이(nsubj), N2:문제가(nsubj) under pred:'아닌가 .a.nin.ga' → default: N1(이것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0068-s182': [('deprel', 1, 'nsubj:outer')],

    # MH2_0068-s2 [train]
    # TEXT: 한, 중, 일 세 나라의 문화를 비교하면 특히 기층문화에서 한국과 일본이 유사점이 많고, 중국과는 더 큰 차이를 보이고 있다.
    # TRANSLIT: han , jung , il se na.ra.yi mun.hwa.reul bi.gyo.ha.myeon teug.hi gi.cheung.mun.hwa.e.seo han.gug.gwa il.bon.i yu.sa.jeom.i manh.go , jung.gug.gwa.neun deo keun cha.i.reul bo.i.go iss.da
    # ENGLISH: Comparing the cultures of the three countries of Korea, China, and Japan, especially in base culture, Korea and Japan show many similarities, while showing greater differences with China.
    # CONFLICT: N1:한국과(nsubj), N2:유사점이(nsubj) under pred:'많고 .manh.go' → default: N1(한국과)→nsubj:outer [NEEDS REVIEW]
    'MH2_0068-s2': [('deprel', 12, 'nsubj:outer')],

    # MH2_0068-s27 [train]
    # TEXT: 일본의 식탁이 여러 가지 음식을 나열한 화려함이 특색이라면, 한국의 특징은 여러 가지를 한 곳에 넣어 섞고 비비는 비빔밥이나 설렁탕이 한국적인 것이라 하겠다.
    # TRANSLIT: il.bon.yi sig.tag.i yeo.reo ga.ji eum.sig.eul na.yeol.han hwa.ryeo.ham.i teug.saeg.i.ra.myeon , han.gug.yi teug.jing.eun yeo.reo ga.ji.reul han gos.e neoh.eo seogg.go bi.bi.neun bi.bim.bab.i.na seol.reong.tang.i han.gug.jeog.in geos.i.ra ha.gess.da
    # ENGLISH: If the characteristic of the Japanese table is its splendor in arranging various foods, Korea's characteristic would be bibimbap, where various things are put together, mixed and stirred, or seolleongtang (ox bone soup).
    # CONFLICT: N1:식탁이(nsubj), N2:화려함이(nsubj) under pred:'특색이라면 .teug.saeg.i.ra.myeon' → default: N1(식탁이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0068-s27': [('deprel', 2, 'nsubj:outer')],

    # MH2_0068-s312 [train]
    # TEXT: 일본의 다실의 구조가 조선 남방, 특히 전라남도 일대에서 가장 많은 차가 재배되고 있습니다.
    # TRANSLIT: il.bon.yi da.sil.yi gu.jo.ga jo.seon nam.bang , teug.hi jeon.ra.nam.do il.dae.e.seo ga.jang manh.eun cha.ga jae.bae.doe.go iss.seub.ni.da
    # ENGLISH: The structure of Japan's tea rooms is in the area where the most tea is grown in the southern part of Joseon, especially throughout the Jeollanam-do region.
    # CONFLICT: N1:구조가(nsubj), N2:차가(nsubj) under pred:'재배되고 .jae.bae.doe.go' → default: N1(구조가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0068-s312': [('deprel', 3, 'nsubj:outer')],

    # MH2_0068-s407 [train]
    # TEXT: 요컨대 막부와 각 번의 생존이 최대목표가 된다.
    # TRANSLIT: yo.keon.dae mag.bu.wa gag beon.yi saeng.jon.i choe.dae.mog.pyo.ga doen.da
    # ENGLISH: In short, survival of the shogunate and each domain becomes the greatest goal.
    # CONFLICT: N1:생존이(nsubj), N2:최대목표가(csubj) under pred:'된다 .doen.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0068-s407': [('deprel', 5, 'nsubj:outer')],

    # MH2_0068-s417 [train]
    # TEXT: 주자학의 윤리문제가 당쟁의 씨가 되었고 중앙의 관료 사이에 투쟁이 생겼다.
    # TRANSLIT: ju.ja.hag.yi yun.ri.mun.je.ga dang.jaeng.yi ssi.ga doe.eoss.go jung.ang.yi gwan.ryo sa.i.e tu.jaeng.i saeng.gyeoss.da
    # ENGLISH: The ethical issues of Neo-Confucianism became the seeds of factional strife, and conflicts arose among central bureaucrats.
    # CONFLICT: N1:윤리문제가(nsubj), N2:씨가(csubj) under pred:'되었고 .doe.eoss.go' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0068-s417': [('deprel', 2, 'nsubj:outer')],

    # MH2_0068-s430 [train]
    # TEXT: 군사조직은 가로사회로 계급의식과 분수를 지키며 주군에 대한 헌신이 중요한 미덕이 된다.
    # TRANSLIT: gun.sa.jo.jig.eun ga.ro.sa.hoe.ro gye.geub.yi.sig.gwa bun.su.reul ji.ki.myeo ju.gun.e dae.han heon.sin.i jung.yo.han mi.deog.i doen.da
    # ENGLISH: Military organization is a hierarchical society where class consciousness and knowing one's place are upheld, and devotion to one's lord becomes an important virtue.
    # CONFLICT: N1:헌신이(nsubj), N2:미덕이(csubj) under pred:'된다 .doen.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0068-s430': [('deprel', 8, 'nsubj:outer')],

    # MH2_0068-s442 [train]
    # TEXT: 조선에서는 가문에 효자비가 세워지는 것을 자랑으로 삼았고, 또 그것이 후손들에게 스스로의 사회적 지위를 높이는 자료가 된다고 믿는 것도 같은 사조이다.
    # TRANSLIT: jo.seon.e.seo.neun ga.mun.e hyo.ja.bi.ga se.weo.ji.neun geos.eul ja.rang.eu.ro sam.ass.go , ddo geu.geos.i hu.son.deul.e.ge seu.seu.ro.yi sa.hoe.jeog ji.wi.reul nop.i.neun ja.ryo.ga doen.da.go mid.neun geos.do gat.eun sa.jo.i.da
    # ENGLISH: In Joseon, it was a source of pride to have a memorial stone for a filial son erected in the family, and believing that it serves as material for descendants to raise their own social status is of the same ideological trend.
    # CONFLICT: N1:그것이(nsubj), N2:자료가(csubj) under pred:'된다고 .doen.da.go' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0068-s442': [('deprel', 10, 'nsubj:outer')],

    # MH2_0068-s477 [train]
    # TEXT: 근세 이후 조선 주자학이 매개가 되어 피차의 윤리관에 공통의 기반을 갖게 된다.
    # TRANSLIT: geun.se i.hu jo.seon ju.ja.hag.i mae.gae.ga doe.eo pi.cha.yi yun.ri.gwan.e gong.tong.yi gi.ban.eul gaj.ge doen.da
    # ENGLISH: Since modern times, Korean Neo-Confucianism served as a medium, providing a common foundation for the ethical views of both sides.
    # CONFLICT: N1:주자학이(nsubj), N2:매개가(csubj) under pred:'되어 .doe.eo' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0068-s477': [('deprel', 4, 'nsubj:outer')],

    # MH2_0068-s63 [train]
    # TEXT: 이것과는 달리 내열형이란 마치 세포가 분열하듯 속에서 방이 두 개가 세 개로 되며, 밖의 벽이 두껍고 속의 방과 방 사이는 벽이 없거나 있어도 약한 것이다.
    # TRANSLIT: i.geos.gwa.neun dal.ri nae.yeol.hyeong.i.ran ma.chi se.po.ga bun.yeol.ha.deus sog.e.seo bang.i du gae.ga se gae.ro doe.myeo , bagg.yi byeog.i du.ggeob.go sog.yi bang.gwa bang sa.i.neun byeog.i eobs.geo.na iss.eo.do yag.han geos.i.da
    # ENGLISH: In contrast, the endothermic type is like a cell dividing from within, where rooms multiply from two to three, the outer walls are thick, and the walls between the inner rooms are absent or thin if present.
    # CONFLICT: N1:방이(nsubj), N2:개가(nsubj) under pred:'되며 .doe.myeo' → default: N1(방이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0068-s63': [('deprel', 8, 'nsubj:outer')],

    # MH2_0068-s66 [train]
    # TEXT: 이것이 추운 지방이거나 장소가 협소하면 자형이 되어 안마당을 완전히 포위한다.
    # TRANSLIT: i.geos.i chu.un ji.bang.i.geo.na jang.so.ga hyeob.so.ha.myeon ja.hyeong.i doe.eo an.ma.dang.eul wan.jeon.hi po.wi.han.da
    # ENGLISH: In cold regions or where space is narrow, this takes on a square shape, completely surrounding the inner courtyard.
    # CONFLICT: N1:이것이(nsubj), N2:자형이(csubj) under pred:'되어 .doe.eo' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0068-s66': [('deprel', 1, 'nsubj:outer')],

    # MH2_0068-s85 [train]
    # TEXT: 온돌방은 밑에서 열을 발산하는 것이기 때문에 방의 높이가 높은 것보다 낮은 것이 유리하다.
    # TRANSLIT: on.dol.bang.eun mit.e.seo yeol.eul bal.san.ha.neun geos.i.gi ddae.mun.e bang.yi nop.i.ga nop.eun geos.bo.da naj.eun geos.i yu.ri.ha.da
    # ENGLISH: Since an ondol room radiates heat from below, it is more advantageous to have a lower ceiling than a higher one.
    # CONFLICT: N1:높이가(nsubj), N2:것이(nsubj) under pred:'유리하다 .yu.ri.ha.da' → default: N1(높이가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0068-s85': [('deprel', 8, 'nsubj:outer')],

    # MH2_0069-s139 [dev]
    # TEXT: 지식 정보상품이 인기가 있게 되자 그들의 관심은 어느 품목을 상품화하느냐의 문제로 전화되었다.
    # TRANSLIT: ji.sig jeong.bo.sang.pum.i in.gi.ga iss.ge doe.ja geu.deul.yi gwan.sim.eun eo.neu pum.mog.eul sang.pum.hwa.ha.neu.nya.yi mun.je.ro jeon.hwa.doe.eoss.da
    # ENGLISH: Once intellectual and information products became popular, their concern shifted to the problem of which items to commercialize.
    # CONFLICT: N1:정보상품이(nsubj), N2:인기가(nsubj) under pred:'있게 .iss.ge' → default: N1(정보상품이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0069-s139': [('deprel', 2, 'nsubj:outer')],

    # MH2_0069-s141 [dev]
    # TEXT: 산업혁명의 결과로 인쇄술의 발전을 급속히 이룩한 영국에선 1814년 이미 바이런의 소설 '해저' 이 출판 당일 1만 부가 팔려나갔다.
    # TRANSLIT: san.eob.hyeog.myeong.yi gyeol.gwa.ro in.swae.sul.yi bal.jeon.eul geub.sog.hi i.rug.han yeong.gug.e.seon 1814.nyeon i.mi ba.i.reon.yi so.seol ' hae.jeo ' i chul.pan dang.il 1.man bu.ga pal.ryeo.na.gass.da
    # ENGLISH: In England, where printing technology rapidly developed as a result of the Industrial Revolution, Byron's novel had already sold 10,000 copies on the day of publication in 1814.
    # CONFLICT: N1:해저(nsubj), N2:부가(nsubj) under pred:'팔려나갔다 .pal.ryeo.na.gass.da' → default: N1(해저)→nsubj:outer [NEEDS REVIEW]
    'MH2_0069-s141': [('deprel', 13, 'nsubj:outer')],

    # MH2_0069-s174 [dev]
    # TEXT: 즉 인간의 관념, 지식 등은 인간의 노동과정을 통해서만 그것이 비로소 현실적이 되며 노동과정의 결과는 인간의 의식, 관념활동을 그에 맞게 조응시킨다.
    # TRANSLIT: jeug in.gan.yi gwan.nyeom , ji.sig deung.eun in.gan.yi no.dong.gwa.jeong.eul tong.hae.seo.man geu.geos.i bi.ro.so hyeon.sil.jeog.i doe.myeo no.dong.gwa.jeong.yi gyeol.gwa.neun in.gan.yi yi.sig , gwan.nyeom.hwal.dong.eul geu.e maj.ge jo.eung.si.kin.da
    # ENGLISH: In other words, human ideas and knowledge become real only through the human labor process, and the results of the labor process align human consciousness and ideational activity accordingly.
    # CONFLICT: N1:그것이(nsubj), N2:현실적이(csubj) under pred:'되며 .doe.myeo' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0069-s174': [('deprel', 10, 'nsubj:outer')],

    # MH2_0069-s384 [dev]
    # TEXT: 이런 제반요인들이 요인들이 유럽 사회의 발전을 가져오는 데 밑거름이 되었다.
    # TRANSLIT: i.reon je.ban.yo.in.deul.i yo.in.deul.i yu.reob sa.hoe.yi bal.jeon.eul ga.jyeo.o.neun de mit.geo.reum.i doe.eoss.da
    # ENGLISH: These various factors became a foundation for bringing about the development of European society.
    # CONFLICT: N1:요인들이(nsubj), N2:밑거름이(csubj) under pred:'되었다 .doe.eoss.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0069-s384': [('deprel', 3, 'nsubj:outer')],

    # MH2_0069-s426 [dev]
    # TEXT: 즉, 면죄부판매의 부당성을 항의하고자 발표한 '95 개조의 반박문' 이 당시 민중들의 호응을 받아 개혁운동의 도화선이 되었다.
    # TRANSLIT: jeug , myeon.joe.bu.pan.mae.yi bu.dang.seong.eul hang.yi.ha.go.ja bal.pyo.han ' 95 gae.jo.yi ban.bag.mun ' i dang.si min.jung.deul.yi ho.eung.eul bad.a gae.hyeog.un.dong.yi do.hwa.seon.i doe.eoss.da
    # ENGLISH: That is, the '95 Theses' published to protest the injustice of indulgence sales received popular support and became the trigger for the Reformation movement.
    # CONFLICT: N1:반박문(nsubj), N2:도화선이(csubj) under pred:'되었다 .doe.eoss.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0069-s426': [('deprel', 10, 'nsubj:outer')],

    # MH2_0069-s7 [dev]
    # TEXT: 다시 말하면 출판에 관한 연구도 사회적 제관계 속에서 이루어질 때만이 진정한 학문이 될 수 있다.
    # TRANSLIT: da.si mal.ha.myeon chul.pan.e gwan.han yeon.gu.do sa.hoe.jeog je.gwan.gye sog.e.seo i.ru.eo.jil ddae.man.i jin.jeong.han hag.mun.i doel su iss.da
    # ENGLISH: In other words, research on publishing can become true scholarship only when it is conducted within social relations.
    # CONFLICT: N1:때만이(nsubj), N2:학문이(csubj) under pred:'될 .doel' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0069-s7': [('deprel', 10, 'nsubj:outer')],

    # MH2_0070-s100 [test]
    # TEXT: 독일, 미국과 한국은 45 54 세 가구주의 가정이 식료품지출 규모가 큰 반면 일본은 30대 중반에서 40대 중반까지의 가구가 가장 높다.
    # TRANSLIT: dog.il , mi.gug.gwa han.gug.eun 45 54 se ga.gu.ju.yi ga.jeong.i sig.ryo.pum.ji.chul gyu.mo.ga keun ban.myeon il.bon.eun 30.dae jung.ban.e.seo 40.dae jung.ban.gga.ji.yi ga.gu.ga ga.jang nop.da
    # ENGLISH: Germany, the United States, and Korea show the largest household food expenditure among 45–54-year-old heads of household, while Japan shows the highest among households with heads in their mid-30s to mid-40s.
    # CONFLICT: N1:가정이(nsubj), N2:규모가(nsubj) under pred:'큰 .keun' → default: N1(가정이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0070-s100': [('deprel', 9, 'nsubj:outer')],

    # MH2_0070-s58 [test]
    # TEXT: 이는 가구당 평균인원수의 변화와 맞물려 나타나 소비지출의 증가가 가구인원의 증가와 높은 관련이 있음을 보여주고 있다.
    # TRANSLIT: i.neun ga.gu.dang pyeong.gyun.in.weon.su.yi byeon.hwa.wa maj.mul.ryeo na.ta.na so.bi.ji.chul.yi jeung.ga.ga ga.gu.in.weon.yi jeung.ga.wa nop.eun gwan.ryeon.i iss.eum.eul bo.yeo.ju.go iss.da
    # ENGLISH: This appears in conjunction with changes in the average number of household members, showing that increases in consumer spending are highly correlated with increases in household members.
    # CONFLICT: N1:증가가(nsubj), N2:관련이(nsubj) under pred:'있음을 .iss.eum.eul' → default: N1(증가가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0070-s58': [('deprel', 8, 'nsubj:outer')],

    # MH2_0071-s255 [train]
    # TEXT: 더욱이 그는 추상적인 언어체계 (랑그) 와 구체적인 언어행위 (파롤) 를 엄격히 구분하여 오직 랑그만이 언어학의 대상이 될 수 있다고 주장하였다.
    # TRANSLIT: deo.ug.i geu.neun chu.sang.jeog.in eon.eo.che.gye ( rang.geu ) wa gu.che.jeog.in eon.eo.haeng.wi ( pa.rol ) reul eom.gyeog.hi gu.bun.ha.yeo o.jig rang.geu.man.i eon.eo.hag.yi dae.sang.i doel su iss.da.go ju.jang.ha.yeoss.da
    # ENGLISH: Moreover, he strictly distinguished between abstract language system (langue) and concrete language behavior (parole), claiming that only langue can be the object of linguistics.
    # CONFLICT: N1:랑그만이(nsubj), N2:대상이(nsubj) under pred:'될 .doel' → default: N1(랑그만이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0071-s255': [('deprel', 18, 'nsubj:outer')],

    # MH2_0071-s94 [train]
    # TEXT: 1989년 카네기 재단은 미국 대학교수들에게 신입생으로 등록하는 학생들이 과연 수학능력이 있다고 생각하느냐는 질문을 한 적이 있다.
    # TRANSLIT: 1989.nyeon ka.ne.gi jae.dan.eun mi.gug dae.hag.gyo.su.deul.e.ge sin.ib.saeng.eu.ro deung.rog.ha.neun hag.saeng.deul.i gwa.yeon su.hag.neung.ryeog.i iss.da.go saeng.gag.ha.neu.nya.neun jil.mun.eul han jeog.i iss.da
    # ENGLISH: In 1989, the Carnegie Foundation asked American university professors whether they thought incoming students were academically capable.
    # CONFLICT: N1:학생들이(nsubj), N2:수학능력이(nsubj) under pred:'있다고 .iss.da.go' → default: N1(학생들이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0071-s94': [('deprel', 8, 'nsubj:outer')],

    # MH2_0071-s95 [train]
    # TEXT: 이 질문에 대하여 무려 64퍼센트에 달하는 대학교수들은 신입생들이 글을 읽고 쓰는 능력에 있어서 대학 수학능력이 결여되어 있다고 응답하였다.
    # TRANSLIT: i jil.mun.e dae.ha.yeo mu.ryeo 64.peo.sen.teu.e dal.ha.neun dae.hag.gyo.su.deul.eun sin.ib.saeng.deul.i geul.eul irg.go sseu.neun neung.ryeog.e iss.eo.seo dae.hag su.hag.neung.ryeog.i gyeol.yeo.doe.eo iss.da.go eung.dab.ha.yeoss.da
    # ENGLISH: In response to this question, no fewer than 64 percent of university professors answered that incoming students lacked the academic ability for university studies in reading and writing.
    # CONFLICT: N1:신입생들이(nsubj), N2:수학능력이(nsubj) under pred:'결여되어 .gyeol.yeo.doe.eo' → default: N1(신입생들이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0071-s95': [('deprel', 8, 'nsubj:outer')],

    # MH2_0072-s111 [train]
    # TEXT: 이러한 의문이 제기되며 규슈가 그 시험장이 되었다.
    # TRANSLIT: i.reo.han yi.mun.i je.gi.doe.myeo gyu.syu.ga geu si.heom.jang.i doe.eoss.da
    # ENGLISH: As such questions arose, Kyushu became the testing ground.
    # CONFLICT: N1:규슈가(nsubj), N2:시험장이(csubj) under pred:'되었다 .doe.eoss.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0072-s111': [('deprel', 4, 'nsubj:outer')],

    # MH2_0072-s33 [train]
    # TEXT: 15세에 야쿠자 세계에 들어와 견습생으로 10년을 보낸 이 고아 소년이 후일 일본 야쿠자사 (史) 에 남는 최고의 오야붕이 된 것이다.
    # TRANSLIT: 15.se.e ya.ku.ja se.gye.e deul.eo.wa gyeon.seub.saeng.eu.ro 10.nyeon.eul bo.naen i go.a so.nyeon.i hu.il il.bon ya.ku.ja.sa ( shǐ ) e nam.neun choe.go.yi o.ya.bung.i doen geos.i.da
    # ENGLISH: This orphan boy, who entered the yakuza world at 15 and spent 10 years as an apprentice, later became the greatest oyabun to be remembered in the history of Japanese yakuza.
    # CONFLICT: N1:소년이(nsubj), N2:오야붕이(csubj) under pred:'된 .doen' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0072-s33': [('deprel', 10, 'nsubj:outer')],

    # MH2_0072-s38 [train]
    # TEXT: 그가 그런 젊은 나이에 조장이 될 수 있었다는 얘기는 당시의 야마구치 조직이란 것이 보잘것없는 조무래기 단체였다는 것을 의미한다.
    # TRANSLIT: geu.ga geu.reon jeorm.eun na.i.e jo.jang.i doel su iss.eoss.da.neun yae.gi.neun dang.si.yi ya.ma.gu.chi jo.jig.i.ran geos.i bo.jal.geos.eobs.neun jo.mu.rae.gi dan.che.yeoss.da.neun geos.eul yi.mi.han.da
    # ENGLISH: The fact that he was able to become a group leader at such a young age means that the Yamaguchi organization of that time was an insignificant ragtag group.
    # CONFLICT: N1:그가(nsubj), N2:조장이(csubj) under pred:'될 .doel' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0072-s38': [('deprel', 1, 'nsubj:outer')],

    # MH2_0072-s419 [train]
    # TEXT: 하토야마가 수상이 된 것은 물론이다.
    # TRANSLIT: ha.to.ya.ma.ga su.sang.i doen geos.eun mul.ron.i.da
    # ENGLISH: It goes without saying that Hatoyama became prime minister.
    # CONFLICT: N1:하토야마가(nsubj), N2:수상이(csubj) under pred:'된 .doen' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0072-s419': [('deprel', 1, 'nsubj:outer')],

    # MH2_0072-s443 [train]
    # TEXT: 그러나 이 때쯤엔 야마모토 장군이 생각이 바뀌어 있었다.
    # TRANSLIT: geu.reo.na i ddae.jjeum.en ya.ma.mo.to jang.gun.i saeng.gag.i ba.ggwi.eo iss.eoss.da
    # ENGLISH: By this time, however, General Yamamoto had a change of heart.
    # CONFLICT: N1:장군이(nsubj), N2:생각이(nsubj) under pred:'바뀌어 .ba.ggwi.eo' → default: N1(장군이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0072-s443': [('deprel', 5, 'nsubj:outer')],

    # MH2_0072-s455 [train]
    # TEXT: 자위대가 국군이 되는 날은 없어져 버린 것이다.
    # TRANSLIT: ja.wi.dae.ga gug.gun.i doe.neun nal.eun eobs.eo.jyeo beo.rin geos.i.da
    # ENGLISH: The day when the Self-Defense Forces would become the national army has vanished.
    # CONFLICT: N1:자위대가(nsubj), N2:국군이(csubj) under pred:'되는 .doe.neun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0072-s455': [('deprel', 1, 'nsubj:outer')],

    # MH2_0072-s514 [train]
    # TEXT: 전 일본인이 그의 팬이 되었고, 스모를 좋아하건 싫어하건 일본인은 누구나 다카하나다를 일본의 영웅으로 추켜세웠다.
    # TRANSLIT: jeon il.bon.in.i geu.yi paen.i doe.eoss.go , seu.mo.reul joh.a.ha.geon sirh.eo.ha.geon il.bon.in.eun nu.gu.na da.ka.ha.na.da.reul il.bon.yi yeong.ung.eu.ro chu.kyeo.se.weoss.da
    # ENGLISH: All Japanese became his fans, and whether they liked sumo or not, every Japanese praised Takahanada as Japan's hero.
    # CONFLICT: N1:일본인이(nsubj), N2:팬이(csubj) under pred:'되었고 .doe.eoss.go' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0072-s514': [('deprel', 2, 'nsubj:outer')],

    # MH2_0072-s538 [train]
    # TEXT: 보통 150킬로그램에서 200킬로그램에 이르는 그들의 육체는 스무 살 후반까지 현역을 지탱하는 것이 보통 고역이 아니다.
    # TRANSLIT: bo.tong 150.kil.ro.geu.raem.e.seo 200.kil.ro.geu.raem.e i.reu.neun geu.deul.yi yug.che.neun seu.mu sal hu.ban.gga.ji hyeon.yeog.eul ji.taeng.ha.neun geos.i bo.tong go.yeog.i a.ni.da
    # ENGLISH: Their bodies, usually weighing 150 to 200 kilograms, find it no easy feat to sustain active competition into their late twenties.
    # CONFLICT: N1:것이(nsubj), N2:고역이(csubj) under pred:'아니다 .a.ni.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0072-s538': [('deprel', 12, 'nsubj:outer')],

    # MH2_0072-s565 [train]
    # TEXT: 이젠 다카하나다가 요코쓰나가 되어도 그 반응은 예전의 그것이 아닐 것이다.
    # TRANSLIT: i.jen da.ka.ha.na.da.ga yo.ko.sseu.na.ga doe.eo.do geu ban.eung.eun ye.jeon.yi geu.geos.i a.nil geos.i.da
    # ENGLISH: Now, even if Takahanada becomes yokozuna, the reaction will not be what it once was.
    # CONFLICT: N1:다카하나다가(nsubj), N2:요코쓰나가(csubj) under pred:'되어도 .doe.eo.do' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0072-s565': [('deprel', 2, 'nsubj:outer')],

    # MH2_0072-s657 [train]
    # TEXT: 두 명의 미야자와 중 우미야자와쪽이 미야자와를 깨고 10대 뉴스 톱이 된 건 그런 이유에서다.
    # TRANSLIT: du myeong.yi mi.ya.ja.wa jung u.mi.ya.ja.wa.jjog.i mi.ya.ja.wa.reul ggae.go 10.dae nyu.seu tob.i doen geon geu.reon i.yu.e.seo.da
    # ENGLISH: Of the two Miyazawas, the reason that Umi-Miyazawa broke through Miyazawa and became the top news story is precisely for this reason.
    # CONFLICT: N1:우미야자와쪽이(nsubj), N2:톱이(csubj) under pred:'된 .doen' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0072-s657': [('deprel', 5, 'nsubj:outer')],

    # MH2_0072-s98 [train]
    # TEXT: 어떤 쪽에 보호비를 바칠 것인가 하는 것이 업계 사람들의 고민거리가 되었다.
    # TRANSLIT: eo.ddeon jjog.e bo.ho.bi.reul ba.chil geos.in.ga ha.neun geos.i eob.gye sa.ram.deul.yi go.min.geo.ri.ga doe.eoss.da
    # ENGLISH: Which side to pay protection money to became the concern of people in the industry.
    # CONFLICT: N1:것이(nsubj), N2:고민거리가(csubj) under pred:'되었다 .doe.eoss.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0072-s98': [('deprel', 7, 'nsubj:outer')],

    # MH2_0083-s285 [train]
    # TEXT: 수교 결정이 남북관계 발전에 도움이 되길 기대한다.
    # TRANSLIT: su.gyo gyeol.jeong.i nam.bug.gwan.gye bal.jeon.e do.um.i doe.gil gi.dae.han.da
    # ENGLISH: We hope that the decision to establish diplomatic relations will help the development of inter-Korean relations.
    # CONFLICT: N1:결정이(nsubj), N2:도움이(nsubj) under pred:'되길 .doe.gil' → default: N1(결정이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0083-s285': [('deprel', 2, 'nsubj:outer')],

    # MH2_0083-s412 [train]
    # TEXT: 노 차관이 화장실에서 되돌아 나오면서 그 사람과 시선이 마주치는가 했더니, 노 차관이 얼른 안경을 벗으며 발 아래로 시선을 떨구었다.
    # TRANSLIT: no cha.gwan.i hwa.jang.sil.e.seo doe.dol.a na.o.myeon.seo geu sa.ram.gwa si.seon.i ma.ju.chi.neun.ga haess.deo.ni , no cha.gwan.i eol.reun an.gyeong.eul beos.eu.myeo bal a.rae.ro si.seon.eul ddeol.gu.eoss.da
    # ENGLISH: As Deputy Minister Roh turned around coming out of the restroom and his gaze met that person's, Deputy Minister Roh quickly took off his glasses and cast his gaze down toward the ground.
    # CONFLICT: N1:차관이(nsubj), N2:시선이(nsubj) under pred:'마주치는가 .ma.ju.chi.neun.ga' → default: N1(차관이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0083-s412': [('deprel', 2, 'nsubj:outer')],

    # MH2_0083-s62 [train]
    # TEXT: 내가 어떤 면에서 통일을 위한 속죄양으로 제단에 던져라 하게 되면 내가 얼마든지 그럴 용의가 있습니다.
    # TRANSLIT: nae.ga eo.ddeon myeon.e.seo tong.il.eul wi.han sog.joe.yang.eu.ro je.dan.e deon.jyeo.ra ha.ge doe.myeon nae.ga eol.ma.deun.ji geu.reol yong.yi.ga iss.seub.ni.da
    # ENGLISH: If in some sense I am told to be thrown as a scapegoat for unification onto the altar, I am willing to do so at any time.
    # CONFLICT: N1:내가(nsubj), N2:용의가(nsubj) under pred:'있습니다 .iss.seub.ni.da' → default: N1(내가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0083-s62': [('deprel', 11, 'nsubj:outer')],

    # MH2_0083-s76 [train]
    # TEXT: 이제 농사가 몇 년 동안 계속 풍년이 들어서 쌀이 엄청나게 많습니다.
    # TRANSLIT: i.je nong.sa.ga myeoch nyeon dong.an gye.sog pung.nyeon.i deul.eo.seo ssal.i eom.cheong.na.ge manh.seub.ni.da
    # ENGLISH: Now, farming has had good harvests for several years in a row and there is an enormous amount of rice.
    # CONFLICT: N1:농사가(nsubj), N2:풍년이(nsubj) under pred:'들어서 .deul.eo.seo' → default: N1(농사가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0083-s76': [('deprel', 2, 'nsubj:outer')],

    # MH2_0084-s105 [train]
    # TEXT: 통도사란 이름은 이곳 영취산이 부처님이 설법하시던 인도 영취산과 모습이 통한다 하여 지어졌다고 한다.
    # TRANSLIT: tong.do.sa.ran i.reum.eun i.gos yeong.chwi.san.i bu.cheo.nim.i seol.beob.ha.si.deon in.do yeong.chwi.san.gwa mo.seub.i tong.han.da ha.yeo ji.eo.jyeoss.da.go han.da
    # ENGLISH: It is said that the name Tongdosa was given because the shape of Yeongchwisan here corresponds with the Indian Grdhrakuta where the Buddha taught.
    # CONFLICT: N1:영취산이(nsubj), N2:모습이(nsubj) under pred:'통한다 .tong.han.da' → default: N1(영취산이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0084-s105': [('deprel', 4, 'nsubj:outer')],

    # MH2_0084-s243 [train]
    # TEXT: 이 때문에 학명이 카멜리아가 되었다.
    # TRANSLIT: i ddae.mun.e hag.myeong.i ka.mel.ri.a.ga doe.eoss.da
    # ENGLISH: For this reason, its scientific name became Camellia.
    # CONFLICT: N1:학명이(nsubj), N2:카멜리아가(csubj) under pred:'되었다 .doe.eoss.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0084-s243': [('deprel', 3, 'nsubj:outer')],

    # MH2_0084-s244 [train]
    # TEXT: 동백나무는 수종이 1백 개가 넘어서 수관이 뛰어나고 꽃이 아름다워 인기가 좋다.
    # TRANSLIT: dong.baeg.na.mu.neun su.jong.i 1.baeg gae.ga neom.eo.seo su.gwan.i ddwi.eo.na.go ggoch.i a.reum.da.weo in.gi.ga joh.da
    # ENGLISH: The camellia tree has more than 100 species, with an excellent crown shape and beautiful flowers, making it popular.
    # CONFLICT: N1:수종이(nsubj), N2:개가(nsubj) under pred:'넘어서 .neom.eo.seo' → default: N1(수종이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0084-s244': [('deprel', 2, 'nsubj:outer')],

    # MH2_0091-s12 [train]
    # TEXT: 그는 단호하게 그 소설이 문학이 아니다라고 규정했다.
    # TRANSLIT: geu.neun dan.ho.ha.ge geu so.seol.i mun.hag.i a.ni.da.ra.go gyu.jeong.haess.da
    # ENGLISH: He firmly declared that the novel was not literature.
    # CONFLICT: N1:소설이(nsubj), N2:문학이(nsubj) under pred:'아니다라고 .a.ni.da.ra.go' → default: N1(소설이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0091-s12': [('deprel', 4, 'nsubj:outer')],

    # MH2_0091-s169 [train]
    # TEXT: 조금 고생이 되더라도 나의 부재가 회사일에 차질이 없도록 애써 주기를 새삼 부탁하오.
    # TRANSLIT: jo.geum go.saeng.i doe.deo.ra.do na.yi bu.jae.ga hoe.sa.il.e cha.jil.i eobs.do.rog ae.sseo ju.gi.reul sae.sam bu.tag.ha.o
    # ENGLISH: Even if it is somewhat inconvenient, please make every effort to ensure that my absence does not disrupt company business.
    # CONFLICT: N1:부재가(nsubj), N2:차질이(nsubj) under pred:'없도록 .eobs.do.rog' → default: N1(부재가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0091-s169': [('deprel', 5, 'nsubj:outer')],

    # MH2_0091-s19 [train]
    # TEXT: 우리 문학에서 성적 담론이 본격적인 인간 본질에 대한 탐구의 매개가 된 것은 90년대에 들어서이다.
    # TRANSLIT: u.ri mun.hag.e.seo seong.jeog dam.ron.i bon.gyeog.jeog.in in.gan bon.jil.e dae.han tam.gu.yi mae.gae.ga doen geos.eun 90.nyeon.dae.e deul.eo.seo.i.da
    # ENGLISH: It was in the 1990s that sexual discourse in our literature became a medium for earnest inquiry into the essence of humanity.
    # CONFLICT: N1:담론이(nsubj), N2:매개가(nsubj) under pred:'된 .doen' → default: N1(담론이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0091-s19': [('deprel', 4, 'nsubj:outer')],

    # MH2_0091-s358 [train]
    # TEXT: 아무튼 구치소에서의 생활이 내게 전혀 백해무익한 시간만이 아니라 유의미한 성잘과 자기발견의 기회를 주고 있다는 것을 알아주기 바라오.
    # TRANSLIT: a.mu.teun gu.chi.so.e.seo.yi saeng.hwal.i nae.ge jeon.hyeo baeg.hae.mu.ig.han si.gan.man.i a.ni.ra yu.yi.mi.han seong.jal.gwa ja.gi.bal.gyeon.yi gi.hoe.reul ju.go iss.da.neun geos.eul al.a.ju.gi ba.ra.o
    # ENGLISH: I want you to know that life in the detention center is not entirely a time of no benefit to me, but is giving me a meaningful opportunity for self-reflection and self-discovery.
    # CONFLICT: N1:생활이(nsubj), N2:시간만이(csubj) under pred:'아니라 .a.ni.ra' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0091-s358': [('deprel', 3, 'nsubj:outer')],

    # MH2_0091-s56 [train]
    # TEXT: 당신과 떨어져 지낸 시간이, 쇠창살 바깥으로 밝아오는 여명 속에서 새로운 날을 맞은 것이 벌써 스무날째가 되고 있소.
    # TRANSLIT: dang.sin.gwa ddeol.eo.jyeo ji.naen si.gan.i , soe.chang.sal ba.ggat.eu.ro barg.a.o.neun yeo.myeong sog.e.seo sae.ro.un nal.eul maj.eun geos.i beol.sseo seu.mu.nal.jjae.ga doe.go iss.so
    # ENGLISH: The time spent apart from you — it has already been twenty days since I greeted a new day in the dawn light brightening outside the iron bars.
    # CONFLICT: N1:것이(nsubj), N2:스무날째가(nsubj) under pred:'되고 .doe.go' → default: N1(것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0091-s56': [('deprel', 14, 'nsubj:outer')],

    # MH2_0092-s10 [train]
    # TEXT: 고고학이 현대 과학의 성과라고 하기에는 그들이 사용하는 도구들이 너무나도 보잘것이 없었다.
    # TRANSLIT: go.go.hag.i hyeon.dae gwa.hag.yi seong.gwa.ra.go ha.gi.e.neun geu.deul.i sa.yong.ha.neun do.gu.deul.i neo.mu.na.do bo.jal.geos.i eobs.eoss.da
    # ENGLISH: The tools they used were too insignificant for archaeology to be called an achievement of modern science.
    # CONFLICT: N1:도구들이(nsubj), N2:보잘것이(nsubj) under pred:'없었다 .eobs.eoss.da' → default: N1(도구들이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0092-s10': [('deprel', 8, 'nsubj:outer')],

    # MH2_0092-s166 [train]
    # TEXT: 은의 제후국에 불과하던 서방의 주족이 눈부시게 성장하여 마침내 은을 멸하고 중원의 새로운 지배자가 되었다.
    # TRANSLIT: eun.yi je.hu.gug.e bul.gwa.ha.deon seo.bang.yi ju.jog.i nun.bu.si.ge seong.jang.ha.yeo ma.chim.nae eun.eul myeol.ha.go jung.weon.yi sae.ro.un ji.bae.ja.ga doe.eoss.da
    # ENGLISH: The Zhou people of the west, who had been nothing more than a vassal state of Shang, grew brilliantly and finally destroyed Shang to become the new rulers of the Central Plains.
    # CONFLICT: N1:주족이(nsubj), N2:지배자가(nsubj) under pred:'되었다 .doe.eoss.da' → default: N1(주족이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0092-s166': [('deprel', 5, 'nsubj:outer')],

    # MH2_0092-s229 [train]
    # TEXT: 그러나 월왕 구천과의 싸움에서 손가락을 부상당한 후 이것이 원인이 되어 죽음에 이르렀다.
    # TRANSLIT: geu.reo.na weol.wang gu.cheon.gwa.yi ssa.um.e.seo son.ga.rag.eul bu.sang.dang.han hu i.geos.i weon.in.i doe.eo jug.eum.e i.reu.reoss.da
    # ENGLISH: However, after being injured on a finger in battle with King Goujian of Yue, this became the cause that led to his death.
    # CONFLICT: N1:이것이(nsubj), N2:원인이(csubj) under pred:'되어 .doe.eo' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0092-s229': [('deprel', 8, 'nsubj:outer')],

    # MH2_0092-s261 [train]
    # TEXT: 그러나 전국시대에 이르면, 춘추 말기 강남의 오, 월에서 시작된 평민병사의 보병전이 중심이 되었다.
    # TRANSLIT: geu.reo.na jeon.gug.si.dae.e i.reu.myeon , chun.chu mal.gi gang.nam.yi o , weol.e.seo si.jag.doen pyeong.min.byeong.sa.yi bo.byeong.jeon.i jung.sim.i doe.eoss.da
    # ENGLISH: However, by the Warring States period, infantry warfare with common soldiers — which had begun in Wu and Yue in the south at the end of the Spring and Autumn period — became the center.
    # CONFLICT: N1:보병전이(nsubj), N2:중심이(csubj) under pred:'되었다 .doe.eoss.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0092-s261': [('deprel', 13, 'nsubj:outer')],

    # MH2_0092-s456 [train]
    # TEXT: 모든 것이 당대 최고의 장인의 솜씨가 발휘되었다.
    # TRANSLIT: mo.deun geos.i dang.dae choe.go.yi jang.in.yi som.ssi.ga bal.hwi.doe.eoss.da
    # ENGLISH: Everything displayed the skill of the greatest craftsmen of the era.
    # CONFLICT: N1:것이(nsubj), N2:솜씨가(nsubj) under pred:'발휘되었다 .bal.hwi.doe.eoss.da' → default: N1(것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0092-s456': [('deprel', 2, 'nsubj:outer')],

    # MH2_0094-s1170 [train]
    # TEXT: 탈해가 뒤에 임금 (신라 제 4대) 이 된 것은 초승달터에 산 덕일 것이다.
    # TRANSLIT: tal.hae.ga dwi.e im.geum ( sin.ra je 4.dae ) i doen geos.eun cho.seung.dal.teo.e san deog.il geos.i.da
    # ENGLISH: It is probably due to living on a crescent-shaped site that Talhae later became king (the 4th king of Silla).
    # CONFLICT: N1:탈해가(nsubj), N2:임금(nsubj) under pred:'된 .doen' → default: N1(탈해가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0094-s1170': [('deprel', 1, 'nsubj:outer')],

    # MH2_0094-s1178 [train]
    # TEXT: 집터가 남북이 길고 동서가 좁으면, 처음은 나쁘나 뒤에 잘된다.
    # TRANSLIT: jib.teo.ga nam.bug.i gil.go dong.seo.ga job.eu.myeon , cheo.eum.eun na.bbeu.na dwi.e jal.doen.da
    # ENGLISH: If the house site is long north–south and narrow east–west, things will be bad at first but will turn out well later.
    # CONFLICT: N1:집터가(nsubj), N2:동서가(nsubj) under pred:'좁으면 .job.eu.myeon' → default: N1(집터가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0094-s1178': [('deprel', 1, 'nsubj:outer')],

    # MH2_0094-s1258 [train]
    # TEXT: 무덤 풍수에서도 '묏자리가 소의 형국이면 그 자손이 부자가 된다' 고 이른다.
    # TRANSLIT: mu.deom pung.su.e.seo.do ' moes.ja.ri.ga so.yi hyeong.gug.i.myeon geu ja.son.i bu.ja.ga doen.da ' go i.reun.da
    # ENGLISH: In grave feng shui too, it is said: 'If the grave site is in the shape of an ox, that person's descendants will become wealthy.'
    # CONFLICT: N1:자손이(nsubj), N2:부자가(csubj) under pred:'된다 .doen.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0094-s1258': [('deprel', 8, 'nsubj:outer')],

    # MH2_0094-s131 [train]
    # TEXT: 따라서 한국이 재벌정치 재 실험장이 되었다.
    # TRANSLIT: dda.ra.seo han.gug.i jae.beol.jeong.chi jae sil.heom.jang.i doe.eoss.da
    # ENGLISH: Thus Korea has become an experimental ground for chaebol politics again.
    # CONFLICT: N1:한국이(nsubj), N2:실험장이(csubj) under pred:'되었다 .doe.eoss.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0094-s131': [('deprel', 2, 'nsubj:outer')],

    # MH2_0094-s1430 [train]
    # TEXT: 사람들이 자주 다니면 땅이 다져져서 길이 생기는 것입니다.
    # TRANSLIT: sa.ram.deul.i ja.ju da.ni.myeon ddang.i da.jyeo.jyeo.seo gil.i saeng.gi.neun geos.ib.ni.da
    # ENGLISH: When people frequently pass through, the ground gets compacted and roads form.
    # CONFLICT: N1:사람들이(nsubj), N2:길이(nsubj) under pred:'생기는 .saeng.gi.neun' → default: N1(사람들이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0094-s1430': [('deprel', 1, 'nsubj:outer')],

    # MH2_0094-s1459 [train]
    # TEXT: 신이 몸의 일부가 되도록 신발끈은 신을 발에 꼭 붙게 만드는 일을 합니다.
    # TRANSLIT: sin.i mom.yi il.bu.ga doe.do.rog sin.bal.ggeun.eun sin.eul bal.e ggog but.ge man.deu.neun il.eul hab.ni.da
    # ENGLISH: Shoelaces do the job of making the shoe cling tightly to the foot so that the shoe becomes part of the body.
    # CONFLICT: N1:신이(nsubj), N2:일부가(nsubj) under pred:'되도록 .doe.do.rog' → default: N1(신이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0094-s1459': [('deprel', 1, 'nsubj:outer')],

    # MH2_0094-s1591 [train]
    # TEXT: 컴퍼스가 수평이 되게 하면 바늘은 남과 북을 각각 가리킵니다.
    # TRANSLIT: keom.peo.seu.ga su.pyeong.i doe.ge ha.myeon ba.neul.eun nam.gwa bug.eul gag.gag ga.ri.kib.ni.da
    # ENGLISH: If the compass is made level, the needle points to the south and the north respectively.
    # CONFLICT: N1:컴퍼스가(nsubj), N2:수평이(nsubj) under pred:'되게 .doe.ge' → default: N1(컴퍼스가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0094-s1591': [('deprel', 1, 'nsubj:outer')],

    # MH2_0094-s1609 [train]
    # TEXT: 그렇기 때문에 25,000 분의 1 지도가 50,000 분의 1 지도보다 담긴 내용이 세밀합니다.
    # TRANSLIT: geu.reoh.gi ddae.mun.e 25,000 bun.yi 1 ji.do.ga 50,000 bun.yi 1 ji.do.bo.da dam.gin nae.yong.i se.mil.hab.ni.da
    # ENGLISH: Therefore, a 1:25,000 map contains more detailed content than a 1:50,000 map.
    # CONFLICT: N1:지도가(nsubj), N2:내용이(nsubj) under pred:'세밀합니다 .se.mil.hab.ni.da' → default: N1(지도가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0094-s1609': [('deprel', 6, 'nsubj:outer')],

    # MH2_0094-s167 [train]
    # TEXT: 대통령 선거공약이 내각이 바뀌었다고 해서 하루아침에 물거품이 되자 국민들 사이에는 어떤 정책이 나와도 얼마나 가겠느냐며 의아해 하는 풍조가 생겼다.
    # TRANSLIT: dae.tong.ryeong seon.geo.gong.yag.i nae.gag.i ba.ggwi.eoss.da.go hae.seo ha.ru.a.chim.e mul.geo.pum.i doe.ja gug.min.deul sa.i.e.neun eo.ddeon jeong.chaeg.i na.wa.do eol.ma.na ga.gess.neu.nya.myeo yi.a.hae ha.neun pung.jo.ga saeng.gyeoss.da
    # ENGLISH: When presidential election pledges became worthless overnight because the cabinet changed, a trend arose among the people of wondering how long any policy would last.
    # CONFLICT: N1:선거공약이(nsubj), N2:물거품이(csubj) under pred:'되자 .doe.ja' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0094-s167': [('deprel', 2, 'nsubj:outer')],

    # MH2_0094-s208 [train]
    # TEXT: 어떤 정책이 의견수렴 과정에서 최상이 아닌 차선책이 되었다 하더라도 불확실성시대에 최상의 정책을 모색하기는 참으로 어렵기 때문이다.
    # TRANSLIT: eo.ddeon jeong.chaeg.i yi.gyeon.su.ryeom gwa.jeong.e.seo choe.sang.i a.nin cha.seon.chaeg.i doe.eoss.da ha.deo.ra.do bul.hwag.sil.seong.si.dae.e choe.sang.yi jeong.chaeg.eul mo.saeg.ha.gi.neun cham.eu.ro eo.ryeob.gi ddae.mun.i.da
    # ENGLISH: Even if a certain policy became a second-best option rather than the best in the process of gathering opinions, it is truly difficult to seek the best policy in an era of uncertainty.
    # CONFLICT: N1:정책이(nsubj), N2:차선책이(csubj) under pred:'되었다 .doe.eoss.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0094-s208': [('deprel', 2, 'nsubj:outer')],

    # MH2_0094-s213 [train]
    # TEXT: 더구나 공무원으로 잔뼈를 굳히지 않은 인사가 경제내각의 총수가 될 경우에는 해당부처의 업무를 파악하는 데만 6 개월 이상이 걸린다고 한다.
    # TRANSLIT: deo.gu.na gong.mu.weon.eu.ro jan.bbyeo.reul gud.hi.ji anh.eun in.sa.ga gyeong.je.nae.gag.yi chong.su.ga doel gyeong.u.e.neun hae.dang.bu.cheo.yi eob.mu.reul pa.ag.ha.neun de.man 6 gae.weol i.sang.i geol.rin.da.go han.da
    # ENGLISH: Moreover, when a person who has not established their career as a civil servant becomes the head of the economic cabinet, it reportedly takes more than 6 months just to grasp the operations of the relevant ministry.
    # CONFLICT: N1:인사가(nsubj), N2:총수가(csubj) under pred:'될 .doel' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0094-s213': [('deprel', 6, 'nsubj:outer')],

    # MH2_0094-s242 [train]
    # TEXT: 이승윤씨가 부총리가 되면서 정책기조가 완전히 바뀌었다.
    # TRANSLIT: i.seung.yun.ssi.ga bu.chong.ri.ga doe.myeon.seo jeong.chaeg.gi.jo.ga wan.jeon.hi ba.ggwi.eoss.da
    # ENGLISH: With Lee Seung-yun becoming deputy prime minister, the policy foundation changed completely.
    # CONFLICT: N1:이승윤씨가(nsubj), N2:부총리가(csubj) under pred:'되면서 .doe.myeon.seo' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0094-s242': [('deprel', 1, 'nsubj:outer')],

    # MH2_0094-s276 [train]
    # TEXT: 이 추세대로 간다면 90년대가 미국의 60년대가 되지 않을까 걱정이다.
    # TRANSLIT: i chu.se.dae.ro gan.da.myeon 90.nyeon.dae.ga mi.gug.yi 60.nyeon.dae.ga doe.ji anh.eul.gga geog.jeong.i.da
    # ENGLISH: If this trend continues, I worry that the 1990s will become America's 1960s.
    # CONFLICT: N1:90년대가(nsubj), N2:60년대가(nsubj) under pred:'되지 .doe.ji' → default: N1(90년대가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0094-s276': [('deprel', 4, 'nsubj:outer')],

    # MH2_0094-s281 [train]
    # TEXT: 업종별로는 제조업이 2백 17 건에 5억 8천 1백만 달러로 전체 해외투자에서 차지하는 비중이 건수로 58.4 % 이고 금액기준으로는 53 % 에 달한다.
    # TRANSLIT: eob.jong.byeol.ro.neun je.jo.eob.i 2.baeg 17 geon.e 5.eog 8.cheon 1.baeg.man dal.reo.ro jeon.che hae.oe.tu.ja.e.seo cha.ji.ha.neun bi.jung.i geon.su.ro 58.4 % i.go geum.aeg.gi.jun.eu.ro.neun 53 % e dal.han.da
    # ENGLISH: By sector, manufacturing stood at 217 cases worth $581 million, accounting for 58.4% of total overseas investment by case count and 53% by amount.
    # CONFLICT: N1:제조업이(nsubj), N2:비중이(nsubj) under pred:'달한다 .dal.han.da' → default: N1(제조업이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0094-s281': [('deprel', 2, 'nsubj:outer')],

    # MH2_0094-s290 [train]
    # TEXT: 그 패턴이 88년을 정점으로 비중이 낮아지고 있다.
    # TRANSLIT: geu pae.teon.i 88.nyeon.eul jeong.jeom.eu.ro bi.jung.i naj.a.ji.go iss.da
    # ENGLISH: The pattern shows a declining share with 1988 as the peak.
    # CONFLICT: N1:패턴이(nsubj), N2:비중이(nsubj) under pred:'낮아지고 .naj.a.ji.go' → default: N1(패턴이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0094-s290': [('deprel', 2, 'nsubj:outer')],

    # MH2_0094-s335 [train]
    # TEXT: 그러한 부분에 대한 투자 소홀이 기업 스스로의 발전뿐 아니라 나라 전체의 발전을 깎아내리는 요인이 되고 있는 것이다.
    # TRANSLIT: geu.reo.han bu.bun.e dae.han tu.ja so.hol.i gi.eob seu.seu.ro.yi bal.jeon.bbun a.ni.ra na.ra jeon.che.yi bal.jeon.eul ggagg.a.nae.ri.neun yo.in.i doe.go iss.neun geos.i.da
    # ENGLISH: Neglect of investment in such areas is becoming a factor that undermines not only the development of the companies themselves but the development of the entire country.
    # CONFLICT: N1:소홀이(nsubj), N2:요인이(csubj) under pred:'되고 .doe.go' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0094-s335': [('deprel', 5, 'nsubj:outer')],

    # MH2_0094-s35 [train]
    # TEXT: 인상된 전세값을 마련치 못한 가장이 자살을 하는 심각한 사태가 발생했다.
    # TRANSLIT: in.sang.doen jeon.se.gabs.eul ma.ryeon.chi mos.han ga.jang.i ja.sal.eul ha.neun sim.gag.han sa.tae.ga bal.saeng.haess.da
    # ENGLISH: A serious incident occurred in which a breadwinner who could not afford the increased jeonse deposit committed suicide.
    # CONFLICT: N1:가장이(nsubj), N2:사태가(nsubj) under pred:'발생했다 .bal.saeng.haess.da' → default: N1(가장이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0094-s35': [('deprel', 5, 'nsubj:outer')],

    # MH2_0094-s404 [train]
    # TEXT: 회감으로 쓰이는 돔이 91년 전년보다 57 % 가 증가한 1천 2백만 달러어치가 전량 일본으로부터 수입되었다.
    # TRANSLIT: hoe.gam.eu.ro sseu.i.neun dom.i 91.nyeon jeon.nyeon.bo.da 57 % ga jeung.ga.han 1.cheon 2.baeg.man dal.reo.eo.chi.ga jeon.ryang il.bon.eu.ro.bu.teo su.ib.doe.eoss.da
    # ENGLISH: The dome used for sashimi, worth 12 million dollars — a 57% increase from the previous year in 1991 — was imported entirely from Japan.
    # CONFLICT: N1:돔이(nsubj), N2:달러어치가(nsubj) under pred:'수입되었다 .su.ib.doe.eoss.da' → default: N1(돔이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0094-s404': [('deprel', 3, 'nsubj:outer')],

    # MH2_0094-s535 [train]
    # TEXT: 땀 흘려 일하여 돈을 벌지 않은 불로소득자들의 과소비가 일반서민의 생활에까지 파급되어 과소비문제가 우리 사회의 암적인 존재가 되어 있다.
    # TRANSLIT: ddam heul.ryeo il.ha.yeo don.eul beol.ji anh.eun bul.ro.so.deug.ja.deul.yi gwa.so.bi.ga il.ban.seo.min.yi saeng.hwal.e.gga.ji pa.geub.doe.eo gwa.so.bi.mun.je.ga u.ri sa.hoe.yi am.jeog.in jon.jae.ga doe.eo iss.da
    # ENGLISH: The overconsumption of those who earn unearned income without hard work has spread even to ordinary people's lives, and overconsumption has become a cancerous presence in our society.
    # CONFLICT: N1:과소비문제가(nsubj), N2:존재가(csubj) under pred:'되어 .doe.eo' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0094-s535': [('deprel', 12, 'nsubj:outer')],

    # MH2_0094-s581 [train]
    # TEXT: 지난 89년 한국의 노사분규로 국내생산이 무려 4조 원어치가 차질을 빚었고 수출차질이 12억 달러어치에 달했다.
    # TRANSLIT: ji.nan 89.nyeon han.gug.yi no.sa.bun.gyu.ro gug.nae.saeng.san.i mu.ryeo 4.jo weon.eo.chi.ga cha.jil.eul bij.eoss.go su.chul.cha.jil.i 12.eog dal.reo.eo.chi.e dal.haess.da
    # ENGLISH: In 1989, labor disputes in Korea caused domestic production shortfalls of as much as 4 trillion won, and export shortfalls reached 1.2 billion dollars.
    # CONFLICT: N1:국내생산이(nsubj), N2:원어치가(nsubj) under pred:'빚었고 .bij.eoss.go' → default: N1(국내생산이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0094-s581': [('deprel', 5, 'nsubj:outer')],

    # MH2_0094-s708 [train]
    # TEXT: 관광지 또는 관광자원의 입지가 대중교통 수단으로 접근이 가능할 때 관광활동은 더욱 활발해지고 관광매력도 커지게 된다.
    # TRANSLIT: gwan.gwang.ji ddo.neun gwan.gwang.ja.weon.yi ib.ji.ga dae.jung.gyo.tong su.dan.eu.ro jeob.geun.i ga.neung.hal ddae gwan.gwang.hwal.dong.eun deo.ug hwal.bal.hae.ji.go gwan.gwang.mae.ryeog.do keo.ji.ge doen.da
    # ENGLISH: When a tourist site or tourist resource is accessible by public transportation, tourist activities become more vigorous and tourist appeal also grows.
    # CONFLICT: N1:입지가(nsubj), N2:접근이(nsubj) under pred:'가능할 .ga.neung.hal' → default: N1(입지가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0094-s708': [('deprel', 4, 'nsubj:outer')],

    # MH2_0094-s71 [train]
    # TEXT: 외형적 지표에서 보듯이 노사분규 건수가 과거보다 16 배 37 배가 늘어난 것도 문제지만 그보다는 노사분규 과정에서의 근로의욕 이완현상이다.
    # TRANSLIT: oe.hyeong.jeog ji.pyo.e.seo bo.deus.i no.sa.bun.gyu geon.su.ga gwa.geo.bo.da 16 bae 37 bae.ga neul.eo.nan geos.do mun.je.ji.man geu.bo.da.neun no.sa.bun.gyu gwa.jeong.e.seo.yi geun.ro.yi.yog i.wan.hyeon.sang.i.da
    # ENGLISH: As seen from external indicators, the number of labor disputes increased 16 to 37 times compared to the past, but a more serious issue is the loosening of the will to work during labor disputes.
    # CONFLICT: N1:건수가(nsubj), N2:배가(nsubj) under pred:'늘어난 .neul.eo.nan' → default: N1(건수가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0094-s71': [('deprel', 5, 'nsubj:outer')],

    # MH2_0094-s77 [train]
    # TEXT: 대외적으로는 중국을 비롯한 아세안 국가들이 저임금을 바탕으로 값싼 제품을 선진시장에 내놓음으로써 우리 제품의 가격이 경쟁력이 급속히 약화되었다.
    # TRANSLIT: dae.oe.jeog.eu.ro.neun jung.gug.eul bi.ros.han a.se.an gug.ga.deul.i jeo.im.geum.eul ba.tang.eu.ro gabs.ssan je.pum.eul seon.jin.si.jang.e nae.noh.eum.eu.ro.sseo u.ri je.pum.yi ga.gyeog.i gyeong.jaeng.ryeog.i geub.sog.hi yag.hwa.doe.eoss.da
    # ENGLISH: Externally, ASEAN countries including China are putting cheap products on advanced markets based on low wages, rapidly weakening the price competitiveness of our products.
    # CONFLICT: N1:가격이(nsubj), N2:경쟁력이(nsubj) under pred:'약화되었다 .yag.hwa.doe.eoss.da' → default: N1(가격이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0094-s77': [('deprel', 14, 'nsubj:outer')],

    # MH2_0094-s919 [train]
    # TEXT: 이 국가기구들의 팽창이 소모사 가문의 치부수단이 되었음은 혁명 이후 명확히 드러나게 되었다.
    # TRANSLIT: i gug.ga.gi.gu.deul.yi paeng.chang.i so.mo.sa ga.mun.yi chi.bu.su.dan.i doe.eoss.eum.eun hyeog.myeong i.hu myeong.hwag.hi deu.reo.na.ge doe.eoss.da
    # ENGLISH: It became clear after the revolution that the expansion of these state apparatuses became a means of enrichment for the Somoza family.
    # CONFLICT: N1:팽창이(nsubj), N2:치부수단이(csubj) under pred:'되었음은 .doe.eoss.eum.eun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0094-s919': [('deprel', 3, 'nsubj:outer')],

    # MH2_0094-s931 [train]
    # TEXT: 두번의 임기에 루이소소모사의 입장을 따르는 정권이 들어섰으며 1967년의 대통령직에 타치토소모사가 나설 것인지가 화제가 되었다.
    # TRANSLIT: du.beon.yi im.gi.e ru.i.so.so.mo.sa.yi ib.jang.eul dda.reu.neun jeong.gweon.i deul.eo.seoss.eu.myeo 1967.nyeon.yi dae.tong.ryeong.jig.e ta.chi.to.so.mo.sa.ga na.seol geos.in.ji.ga hwa.je.ga doe.eoss.da
    # ENGLISH: For two terms, administrations following the position of Luis Somoza came to power, and whether Tachito Somoza would run for the presidency in 1967 became a topic of discussion.
    # CONFLICT: N1:나설(nsubj), N2:화제가(csubj) under pred:'되었다 .doe.eoss.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0094-s931': [('deprel', 11, 'nsubj:outer')],

    # MH2_0105-s8 [train]
    # TEXT: 다시 말해서 민중이 이 사회와 역사의 주인이 되어야 한다는 상황 인식에서 모든 것이 출발되었던 것이다.
    # TRANSLIT: da.si mal.hae.seo min.jung.i i sa.hoe.wa yeog.sa.yi ju.in.i doe.eo.ya han.da.neun sang.hwang in.sig.e.seo mo.deun geos.i chul.bal.doe.eoss.deon geos.i.da
    # ENGLISH: In other words, everything started from the situational awareness that the people must become the masters of this society and history.
    # CONFLICT: N1:민중이(nsubj), N2:주인이(nsubj) under pred:'되어야 .doe.eo.ya' → default: N1(민중이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0105-s8': [('deprel', 3, 'nsubj:outer')],

    # MH2_0110-s191 [test]
    # TEXT: 이것이 베스트 셀러가 되었다.
    # TRANSLIT: i.geos.i be.seu.teu sel.reo.ga doe.eoss.da
    # ENGLISH: This became a bestseller.
    # CONFLICT: N1:이것이(nsubj), N2:셀러가(nsubj) under pred:'되었다 .doe.eoss.da' → default: N1(이것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0110-s191': [('deprel', 1, 'nsubj:outer')],

    # MH2_0110-s201 [test]
    # TEXT: 시대는 바뀌어서 영국보다는 일본이 더욱 강자가 되었다.
    # TRANSLIT: si.dae.neun ba.ggwi.eo.seo yeong.gug.bo.da.neun il.bon.i deo.ug gang.ja.ga doe.eoss.da
    # ENGLISH: Times changed so that Japan became even more dominant than Britain.
    # CONFLICT: N1:일본이(nsubj), N2:강자가(csubj) under pred:'되었다 .doe.eoss.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0110-s201': [('deprel', 4, 'nsubj:outer')],

    # MH2_0110-s203 [test]
    # TEXT: 그 일본이 대국이 된 것이다.
    # TRANSLIT: geu il.bon.i dae.gug.i doen geos.i.da
    # ENGLISH: That Japan has become a great power.
    # CONFLICT: N1:일본이(nsubj), N2:대국이(nsubj) under pred:'된 .doen' → default: N1(일본이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0110-s203': [('deprel', 2, 'nsubj:outer')],

    # MH2_0110-s214 [test]
    # TEXT: 이것이 지금 도쿄의 핵이 되었다.
    # TRANSLIT: i.geos.i ji.geum do.kyo.yi haeg.i doe.eoss.da
    # ENGLISH: This has now become the core of Tokyo.
    # CONFLICT: N1:이것이(nsubj), N2:핵이(nsubj) under pred:'되었다 .doe.eoss.da' → default: N1(이것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0110-s214': [('deprel', 1, 'nsubj:outer')],

    # MH2_0110-s603 [test]
    # TEXT: 아편 중독으로 폐인이 되어 쓰러지는 중국인이 영국 상인의 관심사가 아니었다.
    # TRANSLIT: a.pyeon jung.dog.eu.ro pye.in.i doe.eo sseu.reo.ji.neun jung.gug.in.i yeong.gug sang.in.yi gwan.sim.sa.ga a.ni.eoss.da
    # ENGLISH: The Chinese falling into ruin from opium addiction was not the concern of British merchants.
    # CONFLICT: N1:중국인이(nsubj), N2:관심사가(nsubj) under pred:'아니었다 .a.ni.eoss.da' → default: N1(중국인이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0110-s603': [('deprel', 6, 'nsubj:outer')],

    # MH2_0110-s76 [test]
    # TEXT: 전제 정치에 대한 민중들의 불만이 무르익을 때마다 왕권은 조금씩 의회로 넘어가고 이것이 일찍부터 의회 제도가 발달한 계기가 된 것이다.
    # TRANSLIT: jeon.je jeong.chi.e dae.han min.jung.deul.yi bul.man.i mu.reu.ig.eul ddae.ma.da wang.gweon.eun jo.geum.ssig yi.hoe.ro neom.eo.ga.go i.geos.i il.jjig.bu.teo yi.hoe je.do.ga bal.dal.han gye.gi.ga doen geos.i.da
    # ENGLISH: Whenever popular discontent with autocratic politics was ripe, royal power gradually transferred to parliament, and this became the catalyst for the early development of the parliamentary system.
    # CONFLICT: N1:이것이(nsubj), N2:계기가(nsubj) under pred:'된 .doen' → default: N1(이것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0110-s76': [('deprel', 12, 'nsubj:outer')],

    # MH2_0110-s89 [test]
    # TEXT: 상당수의 국영 기업체가 민영화되어 경영 개선이 이루어졌다.
    # TRANSLIT: sang.dang.su.yi gug.yeong gi.eob.che.ga min.yeong.hwa.doe.eo gyeong.yeong gae.seon.i i.ru.eo.jyeoss.da
    # ENGLISH: A considerable number of state-owned enterprises were privatized and management improvements were achieved.
    # CONFLICT: N1:기업체가(nsubj), N2:개선이(nsubj) under pred:'이루어졌다 .i.ru.eo.jyeoss.da' → default: N1(기업체가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0110-s89': [('deprel', 3, 'nsubj:outer')],

    # MH2_0112-s15 [train]
    # TEXT: 한 나라의 사회 경제발전 초기에 있어 경제는 아직 농업이 위주가 되고 비교적 적은 비율의 인구가 도시에 살고있다.
    # TRANSLIT: han na.ra.yi sa.hoe gyeong.je.bal.jeon cho.gi.e iss.eo gyeong.je.neun a.jig nong.eob.i wi.ju.ga doe.go bi.gyo.jeog jeog.eun bi.yul.yi in.gu.ga do.si.e sal.go.iss.da
    # ENGLISH: In the early stages of a country's socioeconomic development, the economy is still dominated by agriculture and a relatively small proportion of the population lives in cities.
    # CONFLICT: N1:농업이(nsubj), N2:위주가(csubj) under pred:'되고 .doe.go' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0112-s15': [('deprel', 9, 'nsubj:outer')],

    # MH2_0112-s281 [train]
    # TEXT: 이것은 이들 지방도 출신지도자들이 대한민국 정부직 등용에서 대표성이 낮았음을 보여주고 있다.
    # TRANSLIT: i.geos.eun i.deul ji.bang.do chul.sin.ji.do.ja.deul.i dae.han.min.gug jeong.bu.jig deung.yong.e.seo dae.pyo.seong.i naj.ass.eum.eul bo.yeo.ju.go iss.da
    # ENGLISH: This shows that leaders from these local backgrounds were underrepresented in appointment to government positions in the Republic of Korea.
    # CONFLICT: N1:출신지도자들이(nsubj), N2:대표성이(nsubj) under pred:'낮았음을 .naj.ass.eum.eul' → default: N1(출신지도자들이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0112-s281': [('deprel', 4, 'nsubj:outer')],

    # MH2_0112-s98 [train]
    # TEXT: 그러나 한국에서 지도자가 되려고 하는 사람들에게 정부직이 매력이 있는 또 다른 이유들이 있다.
    # TRANSLIT: geu.reo.na han.gug.e.seo ji.do.ja.ga doe.ryeo.go ha.neun sa.ram.deul.e.ge jeong.bu.jig.i mae.ryeog.i iss.neun ddo da.reun i.yu.deul.i iss.da
    # ENGLISH: However, there are other reasons why government positions are attractive to those who aspire to become leaders in Korea.
    # CONFLICT: N1:정부직이(nsubj), N2:매력이(nsubj) under pred:'있는 .iss.neun' → default: N1(정부직이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0112-s98': [('deprel', 7, 'nsubj:outer')],

    # MH2_0113-s121 [train]
    # TEXT: 유럽이 금세기에 들어와서도 두번씩이나 세계대전의 발화점이 된 것은 이미 알고 있는 바와 같다.
    # TRANSLIT: yu.reob.i geum.se.gi.e deul.eo.wa.seo.do du.beon.ssig.i.na se.gye.dae.jeon.yi bal.hwa.jeom.i doen geos.eun i.mi al.go iss.neun ba.wa gat.da
    # ENGLISH: It is already known that Europe became the flashpoint for world wars twice even in this century.
    # CONFLICT: N1:유럽이(nsubj), N2:발화점이(nsubj) under pred:'된 .doen' → default: N1(유럽이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0113-s121': [('deprel', 1, 'nsubj:outer')],

    # MH2_0113-s157 [train]
    # TEXT: 그러나 이렇게 되기 위해서는 정치의 민주화에 비해 크게 뒤떨어진 경제개혁이 일정수준까지 진척되는 것이 절대적인 조건이 되고 있다.
    # TRANSLIT: geu.reo.na i.reoh.ge doe.gi wi.hae.seo.neun jeong.chi.yi min.ju.hwa.e bi.hae keu.ge dwi.ddeol.eo.jin gyeong.je.gae.hyeog.i il.jeong.su.jun.gga.ji jin.cheog.doe.neun geos.i jeol.dae.jeog.in jo.geon.i doe.go iss.da
    # ENGLISH: However, for this to happen, the absolute condition is that economic reform — which has lagged far behind political democratization — must progress to a certain level.
    # CONFLICT: N1:것이(nsubj), N2:조건이(nsubj) under pred:'되고 .doe.go' → default: N1(것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0113-s157': [('deprel', 13, 'nsubj:outer')],

    # MH2_0113-s54 [train]
    # TEXT: 그리고 중근동의 국경을 자의적으로 결정했는데 이것이 팔레스타인 문제 등 현재의 심각한 분쟁의 근본적인 원인이 되었다.
    # TRANSLIT: geu.ri.go jung.geun.dong.yi gug.gyeong.eul ja.yi.jeog.eu.ro gyeol.jeong.haess.neun.de i.geos.i pal.re.seu.ta.in mun.je deung hyeon.jae.yi sim.gag.han bun.jaeng.yi geun.bon.jeog.in weon.in.i doe.eoss.da
    # ENGLISH: And the borders of the Middle East were arbitrarily determined, and this became the fundamental cause of current serious conflicts such as the Palestinian problem.
    # CONFLICT: N1:이것이(nsubj), N2:원인이(csubj) under pred:'되었다 .doe.eoss.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0113-s54': [('deprel', 6, 'nsubj:outer')],

    # MH2_0113-s71 [train]
    # TEXT: 많은 지역국가, 도시국가로 분열되어 정치적으로 발전이 늦어졌던 독일은 프로이센 정부가 중심이 되어 공업화를 추진했다.
    # TRANSLIT: manh.eun ji.yeog.gug.ga , do.si.gug.ga.ro bun.yeol.doe.eo jeong.chi.jeog.eu.ro bal.jeon.i neuj.eo.jyeoss.deon dog.il.eun peu.ro.i.sen jeong.bu.ga jung.sim.i doe.eo gong.eob.hwa.reul chu.jin.haess.da
    # ENGLISH: Germany, politically lagging behind due to division into many regional and city-states, pursued industrialization with the Prussian government at the center.
    # CONFLICT: N1:정부가(nsubj), N2:중심이(nsubj) under pred:'되어 .doe.eo' → default: N1(정부가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0113-s71': [('deprel', 11, 'nsubj:outer')],

    # MH2_0115-s124 [train]
    # TEXT: 이들 노래는 89, 90 년도 일상가요의 맥을 그대로 계승하고 있으면서도 그 기반이 되는 정서가 약간 차이가 나고 있다.
    # TRANSLIT: i.deul no.rae.neun 89 , 90 nyeon.do il.sang.ga.yo.yi maeg.eul geu.dae.ro gye.seung.ha.go iss.eu.myeon.seo.do geu gi.ban.i doe.neun jeong.seo.ga yag.gan cha.i.ga na.go iss.da
    # ENGLISH: These songs inherit the lineage of everyday songs of '89 and '90, yet the underlying sentiment differs slightly.
    # CONFLICT: N1:정서가(nsubj), N2:차이가(nsubj) under pred:'나고 .na.go' → default: N1(정서가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0115-s124': [('deprel', 15, 'nsubj:outer')],

    # MH2_0115-s26 [train]
    # TEXT: 중산층 출신의 10 대 청소년들이 팬클럽을 조직함으로써 또래집단만의 공동체를 구축하는 것이 대표적인 예가 될 수 있다.
    # TRANSLIT: jung.san.cheung chul.sin.yi 10 dae cheong.so.nyeon.deul.i paen.keul.reob.eul jo.jig.ham.eu.ro.sseo ddo.rae.jib.dan.man.yi gong.dong.che.reul gu.chug.ha.neun geos.i dae.pyo.jeog.in ye.ga doel su iss.da
    # ENGLISH: A representative example is that teenagers from the middle class formed fan clubs, building communities exclusively for peer groups.
    # CONFLICT: N1:것이(nsubj), N2:예가(csubj) under pred:'될 .doel' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0115-s26': [('deprel', 11, 'nsubj:outer')],

    # MH2_0115-s80 [train]
    # TEXT: 이것은 우연이라기보다 이들 노래가 다른 노래에 비해 노동자들의 정서에 부합되는 면이 많았다는 것을 의미한다.
    # TRANSLIT: i.geos.eun u.yeon.i.ra.gi.bo.da i.deul no.rae.ga da.reun no.rae.e bi.hae no.dong.ja.deul.yi jeong.seo.e bu.hab.doe.neun myeon.i manh.ass.da.neun geos.eul yi.mi.han.da
    # ENGLISH: This means that these songs had more aspects that resonated with the sentiments of workers than other songs.
    # CONFLICT: N1:노래가(nsubj), N2:면이(nsubj) under pred:'많았다는 .manh.ass.da.neun' → default: N1(노래가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0115-s80': [('deprel', 4, 'nsubj:outer')],

    # MH2_0116-s64 [train]
    # TEXT: 그러나 그것이 자금조달상 이득이 된다면 약간의 손해를 감수하면서도 주문을 받는 경우가 있다.
    # TRANSLIT: geu.reo.na geu.geos.i ja.geum.jo.dal.sang i.deug.i doen.da.myeon yag.gan.yi son.hae.reul gam.su.ha.myeon.seo.do ju.mun.eul bad.neun gyeong.u.ga iss.da
    # ENGLISH: However, if it proves advantageous in terms of raising funds, there are cases where orders are accepted even while incurring some losses.
    # CONFLICT: N1:그것이(nsubj), N2:이득이(nsubj) under pred:'된다면 .doen.da.myeon' → default: N1(그것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0116-s64': [('deprel', 2, 'nsubj:outer')],

    # MH2_0127-s253 [train]
    # TEXT: 그랬더니 장 선생 대답이 기가 막힌 거예요.
    # TRANSLIT: geu.raess.deo.ni jang seon.saeng dae.dab.i gi.ga mag.hin geo.ye.yo
    # ENGLISH: Then Teacher Jang's answer was astounding.
    # CONFLICT: N1:대답이(nsubj), N2:기가(nsubj) under pred:'막힌 .mag.hin' → default: N1(대답이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0127-s253': [('deprel', 4, 'nsubj:outer')],

    # MH2_0127-s256 [train]
    # TEXT: 그가 꿈 속에서 전 세계의 평화와 행복을 위한 정책을 실시했다고 한다면 우리가 어쩔 도리가 있겠어요?
    # TRANSLIT: geu.ga ggum sog.e.seo jeon se.gye.yi pyeong.hwa.wa haeng.bog.eul wi.han jeong.chaeg.eul sil.si.haess.da.go han.da.myeon u.ri.ga eo.jjeol do.ri.ga iss.gess.eo.yo ?
    # ENGLISH: If he had implemented policies for world peace and happiness in his dream, what could we do about it?
    # CONFLICT: N1:우리가(nsubj), N2:도리가(nsubj) under pred:'있겠어요 .iss.gess.eo.yo' → default: N1(우리가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0127-s256': [('deprel', 12, 'nsubj:outer')],

    # MH2_0127-s307 [train]
    # TEXT: 한데 그 사람 말로는 그게 진짜가 아니라, 유리를 깎아 만든 모조 보석이라는 거에요.
    # TRANSLIT: han.de geu sa.ram mal.ro.neun geu.ge jin.jja.ga a.ni.ra , yu.ri.reul ggagg.a man.deun mo.jo bo.seog.i.ra.neun geo.e.yo
    # ENGLISH: However, according to that person, it was not a real gemstone but an imitation gem made by cutting glass.
    # CONFLICT: N1:그게(nsubj), N2:진짜가(nsubj) under pred:'아니라 .a.ni.ra' → default: N1(그게)→nsubj:outer [NEEDS REVIEW]
    'MH2_0127-s307': [('deprel', 5, 'nsubj:outer')],

    # MH2_0127-s484 [train]
    # TEXT: 데카르트처럼 생각하는 게 한가지 방편이 될 수도 있겠지요.
    # TRANSLIT: de.ka.reu.teu.cheo.reom saeng.gag.ha.neun ge han.ga.ji bang.pyeon.i doel su.do iss.gess.ji.yo
    # ENGLISH: Thinking like Descartes could perhaps be one approach.
    # CONFLICT: N1:게(nsubj), N2:방편이(nsubj) under pred:'될 .doel' → default: N1(게)→nsubj:outer [NEEDS REVIEW]
    'MH2_0127-s484': [('deprel', 3, 'nsubj:outer')],

    # MH2_0132-s110 [train]
    # TEXT: 당신이 배가 고플 경우 만약 필요하다면 당신은 음식물을 얻기 위해서 크게 노력할 것이다.
    # TRANSLIT: dang.sin.i bae.ga go.peul gyeong.u man.yag pil.yo.ha.da.myeon dang.sin.eun eum.sig.mul.eul eod.gi wi.hae.seo keu.ge no.ryeog.hal geos.i.da
    # ENGLISH: If you are hungry and it is necessary, you will make great efforts to obtain food.
    # CONFLICT: N1:당신이(nsubj), N2:배가(nsubj) under pred:'고플 .go.peul' → default: N1(당신이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0132-s110': [('deprel', 1, 'nsubj:outer')],

    # MH2_0132-s111 [train]
    # TEXT: 당신의 자식이 배가 고파 할 경우라면 당신은 한층 더 가만히 있을 수 없다고 느낄지도 모른다.
    # TRANSLIT: dang.sin.yi ja.sig.i bae.ga go.pa hal gyeong.u.ra.myeon dang.sin.eun han.cheung deo ga.man.hi iss.eul su eobs.da.go neu.ggil.ji.do mo.reun.da
    # ENGLISH: If your child is hungry, you may feel even more unable to stay still.
    # CONFLICT: N1:자식이(nsubj), N2:배가(nsubj) under pred:'할 .hal' → default: N1(자식이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0132-s111': [('deprel', 2, 'nsubj:outer')],

    # MH2_0132-s126 [train]
    # TEXT: 그러나 철학을 경멸하는 것도 그것이 체계적이 되는 데까지 발전하면 그 자체가 하나의 철학이 된다.
    # TRANSLIT: geu.reo.na cheol.hag.eul gyeong.myeol.ha.neun geos.do geu.geos.i che.gye.jeog.i doe.neun de.gga.ji bal.jeon.ha.myeon geu ja.che.ga ha.na.yi cheol.hag.i doen.da
    # ENGLISH: The problem of reality is not separate from the problem of knowledge.
    # CONFLICT: N1:그것이(nsubj), N2:체계적이(csubj) under pred:'되는 .doe.neun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    # CONFLICT: N1:자체가(nsubj), N2:철학이(csubj) under pred:'된다 .doen.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0132-s126': [('deprel', 5, 'nsubj:outer'), ('deprel', 11, 'nsubj:outer')],

    # MH2_0132-s222 [train]
    # TEXT: 그러나 이러한 모든 것이 저치와 무슨 관계가 있는가라고 말하는 사람이 있을지도 모른다.
    # TRANSLIT: geu.reo.na i.reo.han mo.deun geos.i jeo.chi.wa mu.seun gwan.gye.ga iss.neun.ga.ra.go mal.ha.neun sa.ram.i iss.eul.ji.do mo.reun.da
    # ENGLISH: However, there may be those who ask: what does all this have to do with politics?
    # CONFLICT: N1:것이(nsubj), N2:관계가(nsubj) under pred:'있는가라고 .iss.neun.ga.ra.go' → default: N1(것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0132-s222': [('deprel', 4, 'nsubj:outer')],

    # MH2_0132-s264 [train]
    # TEXT: 프랑스의 사상가의 제자들 사이에서 볼 수 있었던 것처럼 그것이 광신적이 되면 자유주의적으로 있는 것을 정지해 버린다.
    # TRANSLIT: peu.rang.seu.yi sa.sang.ga.yi je.ja.deul sa.i.e.seo bol su iss.eoss.deon geos.cheo.reom geu.geos.i gwang.sin.jeog.i doe.myeon ja.yu.ju.yi.jeog.eu.ro iss.neun geos.eul jeong.ji.hae beo.rin.da
    # ENGLISH: As seen among the disciples of French thinkers, when it becomes fanatical, one stops being liberal.
    # CONFLICT: N1:그것이(nsubj), N2:광신적이(csubj) under pred:'되면 .doe.myeon' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0132-s264': [('deprel', 9, 'nsubj:outer')],

    # MH2_0145-s106 [train]
    # TEXT: 뒤이어 기원전 58 년에는 허려권거의 아들 기후책이 호한야 선우가 되자 군사를 일으켜 한에 투항한 악연구제를 토벌하였다.
    # TRANSLIT: dwi.i.eo gi.weon.jeon 58 nyeon.e.neun heo.ryeo.gweon.geo.yi a.deul gi.hu.chaeg.i ho.han.ya seon.u.ga doe.ja gun.sa.reul il.eu.kyeo han.e tu.hang.han ag.yeon.gu.je.reul to.beol.ha.yeoss.da
    # ENGLISH: Subsequently in 58 BC, when Gihuochaek, the son of Hülerquanju, became the Huhanye Chanyu, he raised troops to suppress Akyeonjuje who had surrendered to Han.
    # CONFLICT: N1:기후책이(nsubj), N2:선우가(csubj) under pred:'되자 .doe.ja' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0145-s106': [('deprel', 7, 'nsubj:outer')],

    # MH2_0145-s302 [train]
    # TEXT: 기원전 3 세기 이후에는 흉노 귀족층의 출현 및 최고 권력의 형성이 이루어졌기 때문에, 인물사오가 조각이 등장하고 있다.
    # TRANSLIT: gi.weon.jeon 3 se.gi i.hu.e.neun hyung.no gwi.jog.cheung.yi chul.hyeon mich choe.go gweon.ryeog.yi hyeong.seong.i i.ru.eo.jyeoss.gi ddae.mun.e , in.mul.sa.o.ga jo.gag.i deung.jang.ha.go iss.da
    # ENGLISH: After the 3rd century BC, the emergence of the Xiongnu noble class and the formation of supreme power were achieved, and therefore sculptural figures appeared.
    # CONFLICT: N1:인물사오가(nsubj), N2:조각이(nsubj) under pred:'등장하고 .deung.jang.ha.go' → default: N1(인물사오가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0145-s302': [('deprel', 15, 'nsubj:outer')],

    # MH2_0145-s317 [train]
    # TEXT: 흉노는 목축 경제를 바탕으로 하는 생활이 주가 되었다.
    # TRANSLIT: hyung.no.neun mog.chug gyeong.je.reul ba.tang.eu.ro ha.neun saeng.hwal.i ju.ga doe.eoss.da
    # ENGLISH: The Xiongnu's way of life, based on a pastoral economy, became their main livelihood.
    # CONFLICT: N1:생활이(nsubj), N2:주가(csubj) under pred:'되었다 .doe.eoss.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0145-s317': [('deprel', 6, 'nsubj:outer')],

    # MH2_0145-s377 [train]
    # TEXT: 단지, 412 년에서 422 년까지 약 10 년간 그가 훈의 동부 지역 경영에 적극적이었고, 412 년에 비잔틴 사절 올림피오도로스가 카라톤에 파견되었다는 사실 정도가 알려져 있다.
    # TRANSLIT: dan.ji , 412 nyeon.e.seo 422 nyeon.gga.ji yag 10 nyeon.gan geu.ga hun.yi dong.bu ji.yeog gyeong.yeong.e jeog.geug.jeog.i.eoss.go , 412 nyeon.e bi.jan.tin sa.jeol ol.rim.pi.o.do.ro.seu.ga ka.ra.ton.e pa.gyeon.doe.eoss.da.neun sa.sil jeong.do.ga al.ryeo.jyeo iss.da
    # ENGLISH: Only the fact that he was actively engaged in managing the eastern part of the Huns for approximately 10 years from 412 to 422, and that the Byzantine envoy Olympiodorus was dispatched to Charaton in 412, is known.
    # CONFLICT: N1:그가(nsubj), N2:올림피오도로스가(nsubj) under pred:'파견되었다는 .pa.gyeon.doe.eoss.da.neun' → default: N1(그가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0145-s377': [('deprel', 10, 'nsubj:outer')],

    # MH2_0145-s453 [train]
    # TEXT: 결과적으로 이탈리아 서로마 침공으로 로마제국의 병참 기지 역할을 했던 갈리아가 폐허가 되어 로마의 후방 보급로가 차단되었다.
    # TRANSLIT: gyeol.gwa.jeog.eu.ro i.tal.ri.a seo.ro.ma chim.gong.eu.ro ro.ma.je.gug.yi byeong.cham gi.ji yeog.hal.eul haess.deon gal.ri.a.ga pye.heo.ga doe.eo ro.ma.yi hu.bang bo.geub.ro.ga cha.dan.doe.eoss.da
    # ENGLISH: As a result, Gaul, which had served as Rome's logistics base, was devastated by the Western Roman invasion of Italy, cutting off Rome's rear supply lines.
    # CONFLICT: N1:갈리아가(nsubj), N2:폐허가(csubj) under pred:'되어 .doe.eo' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0145-s453': [('deprel', 10, 'nsubj:outer')],

    # MH2_0145-s59 [train]
    # TEXT: 흉노가 한군의 공격을 받아 타격을 입고 예봉이 꺽인 네 차례의 전쟁은 다음과 같다.
    # TRANSLIT: hyung.no.ga han.gun.yi gong.gyeog.eul bad.a ta.gyeog.eul ib.go ye.bong.i ggeog.in ne cha.rye.yi jeon.jaeng.eun da.eum.gwa gat.da
    # ENGLISH: The four wars in which the Xiongnu suffered attacks and setbacks from the Han army, with their edge blunted, are as follows.
    # CONFLICT: N1:흉노가(nsubj), N2:예봉이(nsubj) under pred:'꺽인 .ggeog.in' → default: N1(흉노가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0145-s59': [('deprel', 1, 'nsubj:outer')],

    # MH2_0146-s103 [train]
    # TEXT: 따라서 미래의 노동력을 알아보기 위해서는 앞으로 어느 정도의 인구가 노동을 제공할 의사가 있으며 이들 중 일자리를 갖게 되는 사람은 얼마나 되는 것인지를 파악해야 한다.
    # TRANSLIT: dda.ra.seo mi.rae.yi no.dong.ryeog.eul al.a.bo.gi wi.hae.seo.neun ap.eu.ro eo.neu jeong.do.yi in.gu.ga no.dong.eul je.gong.hal yi.sa.ga iss.eu.myeo i.deul jung il.ja.ri.reul gaj.ge doe.neun sa.ram.eun eol.ma.na doe.neun geos.in.ji.reul pa.ag.hae.ya han.da
    # ENGLISH: Therefore, to understand the future labor force, it is necessary to determine how many people will be willing to provide labor and how many of those will obtain jobs.
    # CONFLICT: N1:인구가(nsubj), N2:의사가(nsubj) under pred:'있으며 .iss.eu.myeo' → default: N1(인구가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0146-s103': [('deprel', 9, 'nsubj:outer')],

    # MH2_0146-s31 [train]
    # TEXT: 또한 개성적이고 다양한 가치관이 정립되어 지역별 개인별로 다양한 문화와 생활방식이 출현할 것이며, 다양한 정보원에 대한 접근이 가능하여 개개인이 선택의 자유와 폭이 확대될 것이다.
    # TRANSLIT: ddo.han gae.seong.jeog.i.go da.yang.han ga.chi.gwan.i jeong.rib.doe.eo ji.yeog.byeol gae.in.byeol.ro da.yang.han mun.hwa.wa saeng.hwal.bang.sig.i chul.hyeon.hal geos.i.myeo , da.yang.han jeong.bo.weon.e dae.han jeob.geun.i ga.neung.ha.yeo gae.gae.in.i seon.taeg.yi ja.yu.wa pog.i hwag.dae.doel geos.i.da
    # ENGLISH: Also, individualistic and diverse values will be established, and diverse cultures and lifestyles will emerge regionally and individually; access to diverse information sources will be possible, expanding individual freedom of choice and range.
    # CONFLICT: N1:개개인이(nsubj), N2:자유와(nsubj) under pred:'확대될 .hwag.dae.doel' → default: N1(개개인이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0146-s31': [('deprel', 19, 'nsubj:outer')],

    # MH2_0147-s101 [train]
    # TEXT: 어떠한 쾌락의 증진이나 고통의 회피가 모두 행복이 되는 것은 아니라고 보아, 행복은 바로 최종목적이며 쾌락으로 구성되어 있되 모든 쾌락의 무차별적 합산은 될 수 없다고 본다.
    # TRANSLIT: eo.ddeo.han kwae.rag.yi jeung.jin.i.na go.tong.yi hoe.pi.ga mo.du haeng.bog.i doe.neun geos.eun a.ni.ra.go bo.a , haeng.bog.eun ba.ro choe.jong.mog.jeog.i.myeo kwae.rag.eu.ro gu.seong.doe.eo iss.doe mo.deun kwae.rag.yi mu.cha.byeol.jeog hab.san.eun doel su eobs.da.go bon.da
    # ENGLISH: Not all increases in pleasure or avoidance of pain constitute happiness; happiness is the ultimate goal and consists of pleasures, but it cannot be the indiscriminate sum of all pleasures.
    # CONFLICT: N1:증진이나(nsubj), N2:행복이(csubj) under pred:'되는 .doe.neun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0147-s101': [('deprel', 3, 'nsubj:outer')],

    # MH2_0147-s110 [train]
    # TEXT: 그러나 Mill이 철학가가 가지는 쾌락이 바보의 쾌락보다 좋다고 할 때는 그것이 본유적으로 보다 가치 있다는 것을 동시에 의미한다.
    # TRANSLIT: geu.reo.na Mill.i cheol.hag.ga.ga ga.ji.neun kwae.rag.i ba.bo.yi kwae.rag.bo.da joh.da.go hal ddae.neun geu.geos.i bon.yu.jeog.eu.ro bo.da ga.chi iss.da.neun geos.eul dong.si.e yi.mi.han.da
    # ENGLISH: However, when Mill says that the pleasure of a philosopher is better than the pleasure of a fool, he simultaneously means that it is inherently more valuable.
    # CONFLICT: N1:Mill이(nsubj), N2:쾌락이(nsubj) under pred:'좋다고 .joh.da.go' → default: N1(Mill이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0147-s110': [('deprel', 2, 'nsubj:outer')],

    # MH2_0147-s124 [train]
    # TEXT: 어떤 행동이 절대적으로 옳다거나 또한 해야 할 의무가 있다고 주장하는 것은 보다 많은 선이 아니면 보다 적은 악이 이루어진다는 것을 말한다.
    # TRANSLIT: eo.ddeon haeng.dong.i jeol.dae.jeog.eu.ro orh.da.geo.na ddo.han hae.ya hal yi.mu.ga iss.da.go ju.jang.ha.neun geos.eun bo.da manh.eun seon.i a.ni.myeon bo.da jeog.eun ag.i i.ru.eo.jin.da.neun geos.eul mal.han.da
    # ENGLISH: To claim that a certain action is absolutely right or that there is an obligation to perform it is to say that more good or less evil will result.
    # CONFLICT: N1:행동이(nsubj), N2:의무가(nsubj) under pred:'있다고 .iss.da.go' → default: N1(행동이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0147-s124': [('deprel', 2, 'nsubj:outer')],

    # MH2_0147-s128 [train]
    # TEXT: 이러한 입장은 무엇이 도덕적 평가의 기준이 되느냐에 대한 해답이 순환논법적으로 추구되는 역설적 성격을 모면해야 하는 문제가 있다.
    # TRANSLIT: i.reo.han ib.jang.eun mu.eos.i do.deog.jeog pyeong.ga.yi gi.jun.i doe.neu.nya.e dae.han hae.dab.i sun.hwan.non.beob.jeog.eu.ro chu.gu.doe.neun yeog.seol.jeog seong.gyeog.eul mo.myeon.hae.ya ha.neun mun.je.ga iss.da
    # ENGLISH: This position faces the problem of having to avoid the paradoxical character in which the answer to what is the criterion of moral evaluation is circularly pursued.
    # CONFLICT: N1:무엇이(nsubj), N2:기준이(csubj) under pred:'되느냐에 .doe.neu.nya.e' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0147-s128': [('deprel', 3, 'nsubj:outer')],

    # MH2_0147-s35 [train]
    # TEXT: 물론 지혜 자체는 수단가치로서 그 자체가 목적이 되는 본유적 가치를 가지는 것은 아니다.
    # TRANSLIT: mul.ron ji.hye ja.che.neun su.dan.ga.chi.ro.seo geu ja.che.ga mog.jeog.i doe.neun bon.yu.jeog ga.chi.reul ga.ji.neun geos.eun a.ni.da
    # ENGLISH: Of course, wisdom itself, as an instrumental value, does not possess intrinsic value that makes it an end in itself.
    # CONFLICT: N1:자체가(nsubj), N2:목적이(csubj) under pred:'되는 .doe.neun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0147-s35': [('deprel', 6, 'nsubj:outer')],

    # MH2_0147-s51 [train]
    # TEXT: 이러한 쾌락주의의 인식론적 기초는 감각적 인지론에 바탕을 두고 있기 때문에 활동적이고 육체적인 감응, 즉 격렬하거나 부드러운 운동만이 행동을 위한 확실한 지침이 된다.
    # TRANSLIT: i.reo.han kwae.rag.ju.yi.yi in.sig.ron.jeog gi.cho.neun gam.gag.jeog in.ji.ron.e ba.tang.eul du.go iss.gi ddae.mun.e hwal.dong.jeog.i.go yug.che.jeog.in gam.eung , jeug gyeog.ryeol.ha.geo.na bu.deu.reo.un un.dong.man.i haeng.dong.eul wi.han hwag.sil.han ji.chim.i doen.da
    # ENGLISH: Because the epistemological foundation of hedonism is based on sensory epistemology, active and physical sensations — i.e., intense or gentle movements — become the reliable guide for action.
    # CONFLICT: N1:감응(nsubj), N2:지침이(csubj) under pred:'된다 .doen.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0147-s51': [('deprel', 13, 'nsubj:outer')],

    # MH2_0147-s52 [train]
    # TEXT: 다시 말하면 쾌락적인 것과 고통스러운 것만이 행동지침이 되며 쾌락은 적극적인 감응이며 단순히 고통의 회피가 아닌 것이다.
    # TRANSLIT: da.si mal.ha.myeon kwae.rag.jeog.in geos.gwa go.tong.seu.reo.un geos.man.i haeng.dong.ji.chim.i doe.myeo kwae.rag.eun jeog.geug.jeog.in gam.eung.i.myeo dan.sun.hi go.tong.yi hoe.pi.ga a.nin geos.i.da
    # ENGLISH: In other words, only what is pleasurable and what is painful serve as behavioral guides, and pleasure is a positive sensation and not merely the avoidance of pain.
    # CONFLICT: N1:것과(nsubj), N2:행동지침이(csubj) under pred:'되며 .doe.myeo' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0147-s52': [('deprel', 4, 'nsubj:outer')],

    # MH2_0147-s57 [train]
    # TEXT: Epicurus 윤리체계는, 쾌락을 최고의 선으로 하는 점은 키레네학파와 같으나, 개인이 느끼는 감정을 기준으로 삼고 개인의 안녕이 모든 인간활동의 대상이 되어야 한다고 주장하는 면에 있어서 특이하다.
    # TRANSLIT: Epicurus yun.ri.che.gye.neun , kwae.rag.eul choe.go.yi seon.eu.ro ha.neun jeom.eun ki.re.ne.hag.pa.wa gat.eu.na , gae.in.i neu.ggi.neun gam.jeong.eul gi.jun.eu.ro sam.go gae.in.yi an.nyeong.i mo.deun in.gan.hwal.dong.yi dae.sang.i doe.eo.ya han.da.go ju.jang.ha.neun myeon.e iss.eo.seo teug.i.ha.da
    # ENGLISH: The Epicurean ethical system is unique in that, while it shares with the Cyrenaics the view of pleasure as the highest good, it takes individual feeling as the criterion and argues that individual well-being should be the object of all human activity.
    # CONFLICT: N1:안녕이(nsubj), N2:대상이(csubj) under pred:'되어야 .doe.eo.ya' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0147-s57': [('deprel', 18, 'nsubj:outer')],

    # MH2_0147-s65 [train]
    # TEXT: 우선 쾌락은 종류와 정도의 차이에 있어서 분류가 다양하다고 보고, 적극적 쾌락의 경우는 욕망에 기인하기 때문에, 소극적 쾌락 즉 고통으로부터의 자유가 쾌락의 진정한 목적이 된다고 본다.
    # TRANSLIT: u.seon kwae.rag.eun jong.ryu.wa jeong.do.yi cha.i.e iss.eo.seo bun.ryu.ga da.yang.ha.da.go bo.go , jeog.geug.jeog kwae.rag.yi gyeong.u.neun yog.mang.e gi.in.ha.gi ddae.mun.e , so.geug.jeog kwae.rag jeug go.tong.eu.ro.bu.teo.yi ja.yu.ga kwae.rag.yi jin.jeong.han mog.jeog.i doen.da.go bon.da
    # ENGLISH: First viewing pleasures as having various classifications in kind and degree, in the case of active pleasure it originates from desire, so passive pleasure — i.e., freedom from pain — is seen as the true goal of pleasure.
    # CONFLICT: N1:쾌락(nsubj), N2:목적이(csubj) under pred:'된다고 .doen.da.go' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0147-s65': [('deprel', 19, 'nsubj:outer')],

    # MH2_0147-s74 [train]
    # TEXT: 덕 자체가 사람을 행복하게 하는 것이 아니라 덕을 행함으로써 오는 쾌락이 삶을 행복하게 한다.
    # TRANSLIT: deog ja.che.ga sa.ram.eul haeng.bog.ha.ge ha.neun geos.i a.ni.ra deog.eul haeng.ham.eu.ro.sseo o.neun kwae.rag.i sarm.eul haeng.bog.ha.ge han.da
    # ENGLISH: It is not virtue itself that makes people happy, but the pleasure that comes from practicing virtue that makes life happy.
    # CONFLICT: N1:자체가(nsubj), N2:것이(nsubj) under pred:'아니라 .a.ni.ra' → default: N1(자체가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0147-s74': [('deprel', 2, 'nsubj:outer')],

    # MH2_0147-s93 [train]
    # TEXT: 否의 극단은 결핍의 악을 범하고 正의 극단은 과잉의 악을 수반하므로 중간만이 옳은 이성이 처방하는 바가 된다.
    # TRANSLIT: fǒu.yi geug.dan.eun gyeol.pib.yi ag.eul beom.ha.go zhèng.yi geug.dan.eun gwa.ing.yi ag.eul su.ban.ha.meu.ro jung.gan.man.i orh.eun i.seong.i cheo.bang.ha.neun ba.ga doen.da
    # ENGLISH: The extreme of negation commits the evil of deficiency, and the extreme of the positive accompanies the evil of excess, so only the middle is what correct reason prescribes.
    # CONFLICT: N1:중간만이(nsubj), N2:바가(csubj) under pred:'된다 .doen.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0147-s93': [('deprel', 11, 'nsubj:outer')],

    # MH2_0148-s359 [train]
    # TEXT: 그런데 그 별이 왜 그렇게 특별한 관심 거리가 되었는지 알 수가 없군요.
    # TRANSLIT: geu.reon.de geu byeol.i wae geu.reoh.ge teug.byeol.han gwan.sim geo.ri.ga doe.eoss.neun.ji al su.ga eobs.gun.yo
    # ENGLISH: But I cannot understand why that star became such a special object of interest.
    # CONFLICT: N1:별이(nsubj), N2:거리가(csubj) under pred:'되었는지 .doe.eoss.neun.ji' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0148-s359': [('deprel', 3, 'nsubj:outer')],

    # MH2_0148-s415 [train]
    # TEXT: 대도시들은 일부가 파괴되어 있었고, 거대한 기계들도 발견되긴 했지만 일부만이 작동이 가능했다.
    # TRANSLIT: dae.do.si.deul.eun il.bu.ga pa.goe.doe.eo iss.eoss.go , geo.dae.han gi.gye.deul.do bal.gyeon.doe.gin haess.ji.man il.bu.man.i jag.dong.i ga.neung.haess.da
    # ENGLISH: The major cities were partially destroyed, and giant machines had been found but only some were operational.
    # CONFLICT: N1:일부만이(nsubj), N2:작동이(nsubj) under pred:'가능했다 .ga.neung.haess.da' → default: N1(일부만이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0148-s415': [('deprel', 10, 'nsubj:outer')],

    # MH2_0148-s464 [train]
    # TEXT: 그러나 어느 편도 자신이 최후의 승리자가 되리라는 희망을 버리지 않았으며, 상대편을 사탄의 후예라고 여기는 데에도 변함이 없었다.
    # TRANSLIT: geu.reo.na eo.neu pyeon.do ja.sin.i choe.hu.yi seung.ri.ja.ga doe.ri.ra.neun hyi.mang.eul beo.ri.ji anh.ass.eu.myeo , sang.dae.pyeon.eul sa.tan.yi hu.ye.ra.go yeo.gi.neun de.e.do byeon.ham.i eobs.eoss.da
    # ENGLISH: However, neither side abandoned the hope of being the final victor, and neither stopped regarding the other side as the offspring of Satan.
    # CONFLICT: N1:자신이(nsubj), N2:승리자가(csubj) under pred:'되리라는 .doe.ri.ra.neun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0148-s464': [('deprel', 4, 'nsubj:outer')],

    # MH2_0148-s475 [train]
    # TEXT: 그 클럽의 회장과 부회장이 싸움을 벌일 때까지는 모든 일이 잘 되어갔다.
    # TRANSLIT: geu keul.reob.yi hoe.jang.gwa bu.hoe.jang.i ssa.um.eul beol.il ddae.gga.ji.neun mo.deun il.i jal doe.eo.gass.da
    # ENGLISH: Everything went well until the president and vice president of that club had a fight.
    # CONFLICT: N1:회장과(nsubj), N2:일이(csubj) under pred:'되어갔다 .doe.eo.gass.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0148-s475': [('deprel', 3, 'nsubj:outer')],

    # MH2_0149-s101 [dev]
    # TEXT: 하지만 분명한 것은 어느 편이 논쟁의 승자가 되더라도 승자는 패자의 주장에 포함된 긍정점을 껴안아야만이 스스로의 결함을 보완하게 된다는 점이다.
    # TRANSLIT: ha.ji.man bun.myeong.han geos.eun eo.neu pyeon.i non.jaeng.yi seung.ja.ga doe.deo.ra.do seung.ja.neun pae.ja.yi ju.jang.e po.ham.doen geung.jeong.jeom.eul ggyeo.an.a.ya.man.i seu.seu.ro.yi gyeol.ham.eul bo.wan.ha.ge doen.da.neun jeom.i.da
    # ENGLISH: However, what is clear is that no matter which side becomes the winner of the debate, the winner must embrace the positive points contained in the loser's argument in order to supplement their own shortcomings.
    # CONFLICT: N1:편이(nsubj), N2:승자가(csubj) under pred:'되더라도 .doe.deo.ra.do' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0149-s101': [('deprel', 5, 'nsubj:outer')],

    # MH2_0159-s135 [dev]
    # TEXT: 이러한 비인간적인 삶의 목록을 인간적인 꿈의 목록으로 환원하고자 하는 것이 금세기 인문주의의 과제가 아닐까요.
    # TRANSLIT: i.reo.han bi.in.gan.jeog.in sarm.yi mog.rog.eul in.gan.jeog.in ggum.yi mog.rog.eu.ro hwan.weon.ha.go.ja ha.neun geos.i geum.se.gi in.mun.ju.yi.yi gwa.je.ga a.nil.gga.yo
    # ENGLISH: Is it not the task of this century's humanism to try to convert this list of inhumane lives into a list of humane dreams?
    # CONFLICT: N1:것이(nsubj), N2:과제가(nsubj) under pred:'아닐까요 .a.nil.gga.yo' → default: N1(것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0159-s135': [('deprel', 10, 'nsubj:outer')],

    # MH2_0159-s159 [dev]
    # TEXT: 하지만, 이러한 것들이 끝내는 결정적인 가치의 지표가 되지 못했던 것도 사실입니다.
    # TRANSLIT: ha.ji.man , i.reo.han geos.deul.i ggeut.nae.neun gyeol.jeong.jeog.in ga.chi.yi ji.pyo.ga doe.ji mos.haess.deon geos.do sa.sil.ib.ni.da
    # ENGLISH: However, it is also true that these things ultimately failed to become decisive value indicators.
    # CONFLICT: N1:것들이(nsubj), N2:지표가(csubj) under pred:'되지 .doe.ji' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0159-s159': [('deprel', 4, 'nsubj:outer')],

    # MH2_0159-s223 [dev]
    # TEXT: 오늘날에도 서정시가 비설화적인 요인이 전제가 되어 노래스런 말투와 결스러운 말씨를 이룩하는 언어적 質을 구현하고 있는 것도 이 때문이다.
    # TRANSLIT: o.neul.nal.e.do seo.jeong.si.ga bi.seol.hwa.jeog.in yo.in.i jeon.je.ga doe.eo no.rae.seu.reon mal.tu.wa gyeol.seu.reo.un mal.ssi.reul i.rug.ha.neun eon.eo.jeog zhì.eul gu.hyeon.ha.go iss.neun geos.do i ddae.mun.i.da
    # ENGLISH: Even today, lyric poetry realizes a linguistic quality that creates a song-like tone and graceful speech, with non-narrative elements as a premise, for this very reason.
    # CONFLICT: N1:요인이(nsubj), N2:전제가(csubj) under pred:'되어 .doe.eo' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0159-s223': [('deprel', 4, 'nsubj:outer')],

    # MH2_0159-s266 [dev]
    # TEXT: 언어가 단순한 의사소통 정보교환의 도구가 아니라 언어를 통해 새로운 삶의 질서와 세계상을 형성할 수 있다는 신뢰감이 부여되기 시작했다.
    # TRANSLIT: eon.eo.ga dan.sun.han yi.sa.so.tong jeong.bo.gyo.hwan.yi do.gu.ga a.ni.ra eon.eo.reul tong.hae sae.ro.un sarm.yi jil.seo.wa se.gye.sang.eul hyeong.seong.hal su iss.da.neun sin.roe.gam.i bu.yeo.doe.gi si.jag.haess.da
    # ENGLISH: A sense of trust began to be conferred that language is not merely a tool for communication and information exchange, but that through language, a new order of life and world image can be formed.
    # CONFLICT: N1:언어가(nsubj), N2:도구가(csubj) under pred:'아니라 .a.ni.ra' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0159-s266': [('deprel', 1, 'nsubj:outer')],

    # MH2_0159-s74 [dev]
    # TEXT: 건전한 평균적 상식이 타매되고 오히려 타락과 저주를 찬미하는 저열한 통속주의가 스스럼없이 신윤리의 척도가 되는 까닭을 나는 알지 못한다.
    # TRANSLIT: geon.jeon.han pyeong.gyun.jeog sang.sig.i ta.mae.doe.go o.hi.ryeo ta.rag.gwa jeo.ju.reul chan.mi.ha.neun jeo.yeol.han tong.sog.ju.yi.ga seu.seu.reom.eobs.i sin.yun.ri.yi cheog.do.ga doe.neun gga.darg.eul na.neun al.ji mos.han.da
    # ENGLISH: I do not know why healthy average common sense is rejected, and instead the lowly vulgarity that praises depravity and curses freely becomes the measure of a new ethics.
    # CONFLICT: N1:통속주의가(nsubj), N2:척도가(csubj) under pred:'되는 .doe.neun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0159-s74': [('deprel', 10, 'nsubj:outer')],

    # MH2_0163-s117 [train]
    # TEXT: 과거의 선거가 관권개입에 의해 그 공정성이 훼손되었다면 오늘의 선거는 금권에 의해 그 공정성이 무너지고 있다.
    # TRANSLIT: gwa.geo.yi seon.geo.ga gwan.gweon.gae.ib.e yi.hae geu gong.jeong.seong.i hwe.son.doe.eoss.da.myeon o.neul.yi seon.geo.neun geum.gweon.e yi.hae geu gong.jeong.seong.i mu.neo.ji.go iss.da
    # ENGLISH: If past elections had their fairness undermined by official interference, today's elections have their fairness being eroded by money.
    # CONFLICT: N1:선거가(nsubj), N2:공정성이(nsubj) under pred:'훼손되었다면 .hwe.son.doe.eoss.da.myeon' → default: N1(선거가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0163-s117': [('deprel', 2, 'nsubj:outer')],

    # MH2_0163-s118 [train]
    # TEXT: 왜 금권선거가 한국선거의 특징이 되겠는가?
    # TRANSLIT: wae geum.gweon.seon.geo.ga han.gug.seon.geo.yi teug.jing.i doe.gess.neun.ga ?
    # ENGLISH: Why would money politics become a characteristic of Korean elections?
    # CONFLICT: N1:금권선거가(nsubj), N2:특징이(nsubj) under pred:'되겠는가 .doe.gess.neun.ga' → default: N1(금권선거가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0163-s118': [('deprel', 2, 'nsubj:outer')],

    # MH2_0163-s121 [train]
    # TEXT: 그러한 나쁜 관행이 유권자들의 의식을 타락시켰고 선거시에 돈이나 이권을 주고 받는 것이 우리 선거문화의 특징이 되어버렸던 것이다.
    # TRANSLIT: geu.reo.han na.bbeun gwan.haeng.i yu.gweon.ja.deul.yi yi.sig.eul ta.rag.si.kyeoss.go seon.geo.si.e don.i.na i.gweon.eul ju.go bad.neun geos.i u.ri seon.geo.mun.hwa.yi teug.jing.i doe.eo.beo.ryeoss.deon geos.i.da
    # ENGLISH: Such bad practices corrupted voters' consciousness, and buying and selling votes or interests during elections had become a characteristic of our election culture.
    # CONFLICT: N1:것이(nsubj), N2:특징이(csubj) under pred:'되어버렸던 .doe.eo.beo.ryeoss.deon' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0163-s121': [('deprel', 12, 'nsubj:outer')],

    # MH2_0163-s224 [train]
    # TEXT: 하부당원들이 지역수준의 정치에 관심이 높을 뿐 아니라 참여의 정도도 높기 때문에 풀뿌리민주주의가 이룩된다.
    # TRANSLIT: ha.bu.dang.weon.deul.i ji.yeog.su.jun.yi jeong.chi.e gwan.sim.i nop.eul bbun a.ni.ra cham.yeo.yi jeong.do.do nop.gi ddae.mun.e pul.bbu.ri.min.ju.ju.yi.ga i.rug.doen.da
    # ENGLISH: Because grassroots members have not only high interest but also high participation in local-level politics, grassroots democracy is achieved.
    # CONFLICT: N1:하부당원들이(nsubj), N2:관심이(nsubj) under pred:'높을 .nop.eul' → default: N1(하부당원들이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0163-s224': [('deprel', 1, 'nsubj:outer')],

    # MH2_0164-s32 [train]
    # TEXT: 경제체제 혹은 경제조직은 본래 무엇인가의 의도를 갖고 사전에 그것이 결정되어야 하는 것은 아니라는 의미에서 그 자체가 목적이 될 수는 없다.
    # TRANSLIT: gyeong.je.che.je hog.eun gyeong.je.jo.jig.eun bon.rae mu.eos.in.ga.yi yi.do.reul gaj.go sa.jeon.e geu.geos.i gyeol.jeong.doe.eo.ya ha.neun geos.eun a.ni.ra.neun yi.mi.e.seo geu ja.che.ga mog.jeog.i doel su.neun eobs.da
    # ENGLISH: An economic system or economic organization, in the sense that it is not something that must be determined in advance with some intention, cannot itself be an end.
    # CONFLICT: N1:자체가(nsubj), N2:목적이(nsubj) under pred:'될 .doel' → default: N1(자체가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0164-s32': [('deprel', 16, 'nsubj:outer')],

    # MH2_0164-s6 [train]
    # TEXT: 동시에 개인단위의 잘 산다는 것이 주요 관심사항이 아니라면 한국사회라는 공동체단위에서 잘 산다 것을 판단하기란 더욱 어렵다.
    # TRANSLIT: dong.si.e gae.in.dan.wi.yi jal san.da.neun geos.i ju.yo gwan.sim.sa.hang.i a.ni.ra.myeon han.gug.sa.hoe.ra.neun gong.dong.che.dan.wi.e.seo jal san.da geos.eul pan.dan.ha.gi.ran deo.ug eo.ryeob.da
    # ENGLISH: At the same time, if the prosperity of individuals is not the primary concern, it is even more difficult to judge what it means to live well at the level of the Korean social community.
    # CONFLICT: N1:것이(nsubj), N2:관심사항이(csubj) under pred:'아니라면 .a.ni.ra.myeon' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0164-s6': [('deprel', 5, 'nsubj:outer')],

    # MH2_0164-s61 [train]
    # TEXT: 경제의 안정은 보다 구체적으로는 인플레 없는 완전 고용을 의미한다는 것이 주류가 되고 있다.
    # TRANSLIT: gyeong.je.yi an.jeong.eun bo.da gu.che.jeog.eu.ro.neun in.peul.re eobs.neun wan.jeon go.yong.eul yi.mi.han.da.neun geos.i ju.ryu.ga doe.go iss.da
    # ENGLISH: The mainstream view is that economic stability more specifically means full employment without inflation.
    # CONFLICT: N1:것이(nsubj), N2:주류가(csubj) under pred:'되고 .doe.go' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0164-s61': [('deprel', 10, 'nsubj:outer')],

    # MH2_0169-s189 [dev]
    # TEXT: 예를 들어 중국의 경우는 오랫동안 정치에서 민주주의가 없었다는 것이 하나의 조건이 된다.
    # TRANSLIT: ye.reul deul.eo jung.gug.yi gyeong.u.neun o.raes.dong.an jeong.chi.e.seo min.ju.ju.yi.ga eobs.eoss.da.neun geos.i ha.na.yi jo.geon.i doen.da
    # ENGLISH: For example, in the case of China, the long absence of democracy in politics is one condition.
    # CONFLICT: N1:것이(nsubj), N2:조건이(nsubj) under pred:'된다 .doen.da' → default: N1(것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0169-s189': [('deprel', 9, 'nsubj:outer')],

    # MH2_0169-s199 [dev]
    # TEXT: 그 결과가 이번 선거에서 나타난 패배의 한 원인이 되었다.
    # TRANSLIT: geu gyeol.gwa.ga i.beon seon.geo.e.seo na.ta.nan pae.bae.yi han weon.in.i doe.eoss.da
    # ENGLISH: The result became one cause of the defeat in this election.
    # CONFLICT: N1:결과가(nsubj), N2:원인이(nsubj) under pred:'되었다 .doe.eoss.da' → default: N1(결과가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0169-s199': [('deprel', 2, 'nsubj:outer')],

    # MH2_0169-s212 [dev]
    # TEXT: 살기가 힘들지요 하는 말로 연설을 시작하는 게 습관이 되어 버렸다.
    # TRANSLIT: sal.gi.ga him.deul.ji.yo ha.neun mal.ro yeon.seol.eul si.jag.ha.neun ge seub.gwan.i doe.eo beo.ryeoss.da
    # ENGLISH: It became a habit to start speeches with the words 'Life is tough, isn't it.'
    # CONFLICT: N1:게(nsubj), N2:습관이(nsubj) under pred:'되어 .doe.eo' → default: N1(게)→nsubj:outer [NEEDS REVIEW]
    'MH2_0169-s212': [('deprel', 7, 'nsubj:outer')],

    # MH2_0169-s336 [dev]
    # TEXT: 그 곳에서 연설을 하려다 보니 도대체 안양시민들에게 안양지역에서 활동한 민중진영이 제대로 도움이 되었던 활동이라고 뭐 하나 자랑할 만한 게 없었다.
    # TRANSLIT: geu gos.e.seo yeon.seol.eul ha.ryeo.da bo.ni do.dae.che an.yang.si.min.deul.e.ge an.yang.ji.yeog.e.seo hwal.dong.han min.jung.jin.yeong.i je.dae.ro do.um.i doe.eoss.deon hwal.dong.i.ra.go mweo ha.na ja.rang.hal man.han ge eobs.eoss.da
    # ENGLISH: When I tried to give a speech there, I couldn't find a single thing to be proud of about the people's camp that had been active in Anyang as being genuinely helpful to Anyang citizens.
    # CONFLICT: N1:민중진영이(nsubj), N2:도움이(nsubj) under pred:'되었던 .doe.eoss.deon' → default: N1(민중진영이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0169-s336': [('deprel', 10, 'nsubj:outer')],

    # MH2_0169-s428 [dev]
    # TEXT: 대기업노동자가 현실운동의 주력이 되어 있지만 그들의 정서가 대변되지 않는다고 하는 것은 우리 운동의 주력을 이루고 있는 각급 조직의 모습에서도 나타난다.
    # TRANSLIT: dae.gi.eob.no.dong.ja.ga hyeon.sil.un.dong.yi ju.ryeog.i doe.eo iss.ji.man geu.deul.yi jeong.seo.ga dae.byeon.doe.ji anh.neun.da.go ha.neun geos.eun u.ri un.dong.yi ju.ryeog.eul i.ru.go iss.neun gag.geub jo.jig.yi mo.seub.e.seo.do na.ta.nan.da
    # ENGLISH: Although large enterprise workers have become the main force of actual movements, the fact that their sentiments are not represented is also reflected in the appearance of organizations at all levels that form the main force of our movement.
    # CONFLICT: N1:대기업노동자가(nsubj), N2:주력이(nsubj) under pred:'되어 .doe.eo' → default: N1(대기업노동자가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0169-s428': [('deprel', 1, 'nsubj:outer')],

    # MH2_0169-s489 [dev]
    # TEXT: 근로대중이 생산수단과 국가권력의 주인이 되는 사회를 만들겠다는 정신은 같을지 모르지만 방법이 다르고 제도가 다르다.
    # TRANSLIT: geun.ro.dae.jung.i saeng.san.su.dan.gwa gug.ga.gweon.ryeog.yi ju.in.i doe.neun sa.hoe.reul man.deul.gess.da.neun jeong.sin.eun gat.eul.ji mo.reu.ji.man bang.beob.i da.reu.go je.do.ga da.reu.da
    # ENGLISH: The spirit of creating a society in which working people become the masters of the means of production and state power may be the same, but the methods are different and the systems are different.
    # CONFLICT: N1:근로대중이(nsubj), N2:주인이(nsubj) under pred:'되는 .doe.neun' → default: N1(근로대중이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0169-s489': [('deprel', 1, 'nsubj:outer')],

    # MH2_0169-s534 [dev]
    # TEXT: 그것은 일본 중소기업과 재벌의 관계가 수직상하 관계가 아니라는 데 있다.
    # TRANSLIT: geu.geos.eun il.bon jung.so.gi.eob.gwa jae.beol.yi gwan.gye.ga su.jig.sang.ha gwan.gye.ga a.ni.ra.neun de iss.da
    # ENGLISH: This lies in the fact that the relationship between Japanese small and medium enterprises and conglomerates is not a vertical hierarchical relationship.
    # CONFLICT: N1:관계가(nsubj), N2:관계가(nsubj) under pred:'아니라는 .a.ni.ra.neun' → default: N1(관계가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0169-s534': [('deprel', 5, 'nsubj:outer')],

    # MH2_0169-s539 [dev]
    # TEXT: 대신 중소기업이 이렇게 되려면 대기업이 중소기업을 착실히 돌본다는 것이 전제가 되어야 한다.
    # TRANSLIT: dae.sin jung.so.gi.eob.i i.reoh.ge doe.ryeo.myeon dae.gi.eob.i jung.so.gi.eob.eul chag.sil.hi dol.bon.da.neun geos.i jeon.je.ga doe.eo.ya han.da
    # ENGLISH: Instead, for small and medium enterprises to become like this, the premise must be that large enterprises carefully look after small and medium enterprises.
    # CONFLICT: N1:것이(nsubj), N2:전제가(nsubj) under pred:'되어야 .doe.eo.ya' → default: N1(것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0169-s539': [('deprel', 9, 'nsubj:outer')],

    # MH2_0169-s549 [dev]
    # TEXT: 그러다가 대기업이 사정이 생겨 돈을 지급하지 못하면 연쇄부도가 난다.
    # TRANSLIT: geu.reo.da.ga dae.gi.eob.i sa.jeong.i saeng.gyeo don.eul ji.geub.ha.ji mos.ha.myeon yeon.swae.bu.do.ga nan.da
    # ENGLISH: But when large enterprises face difficulties and cannot pay, chain bankruptcies occur.
    # CONFLICT: N1:대기업이(nsubj), N2:사정이(nsubj) under pred:'생겨 .saeng.gyeo' → default: N1(대기업이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0169-s549': [('deprel', 2, 'nsubj:outer')],

    # MH2_0169-s572 [dev]
    # TEXT: 또 하나는 은행이 대재벌의 사금고가 되어 있기 때문이다.
    # TRANSLIT: ddo ha.na.neun eun.haeng.i dae.jae.beol.yi sa.geum.go.ga doe.eo iss.gi ddae.mun.i.da
    # ENGLISH: Another reason is that banks have become private coffers of the large conglomerates.
    # CONFLICT: N1:은행이(nsubj), N2:사금고가(nsubj) under pred:'되어 .doe.eo' → default: N1(은행이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0169-s572': [('deprel', 3, 'nsubj:outer')],

    # MH2_0169-s597 [dev]
    # TEXT: 즉 분배, 정의 및 복지실현을 골자로 하는 독일 특유의 사회시장경제가 독일 경제의 대외경쟁력에 최대 자산이 되고 있다는 것이다.
    # TRANSLIT: jeug bun.bae , jeong.yi mich bog.ji.sil.hyeon.eul gol.ja.ro ha.neun dog.il teug.yu.yi sa.hoe.si.jang.gyeong.je.ga dog.il gyeong.je.yi dae.oe.gyeong.jaeng.ryeog.e choe.dae ja.san.i doe.go iss.da.neun geos.i.da
    # ENGLISH: That is, Germany's unique social market economy — which has as its core distribution, justice, and welfare realization — is becoming the greatest asset of Germany's external competitiveness.
    # CONFLICT: N1:사회시장경제가(nsubj), N2:자산이(nsubj) under pred:'되고 .doe.go' → default: N1(사회시장경제가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0169-s597': [('deprel', 11, 'nsubj:outer')],

    # MH2_0169-s628 [dev]
    # TEXT: 국민경쟁력은 없고 국내시장을 상대하자니 재벌 물건을 사줘야 할 중소기업과 노동자들이 재벌이 만든 물건을 살 만큼 여유가 있지 않은 것이다.
    # TRANSLIT: gug.min.gyeong.jaeng.ryeog.eun eobs.go gug.nae.si.jang.eul sang.dae.ha.ja.ni jae.beol mul.geon.eul sa.jweo.ya hal jung.so.gi.eob.gwa no.dong.ja.deul.i jae.beol.i man.deun mul.geon.eul sal man.keum yeo.yu.ga iss.ji anh.eun geos.i.da
    # ENGLISH: There is no national competitiveness, and trying to serve the domestic market means that the small and medium enterprises and workers who should buy conglomerate goods don't have enough margin to buy what the conglomerates produce.
    # CONFLICT: N1:중소기업과(nsubj), N2:여유가(nsubj) under pred:'있지 .iss.ji' → default: N1(중소기업과)→nsubj:outer [NEEDS REVIEW]
    'MH2_0169-s628': [('deprel', 9, 'nsubj:outer')],

    # MH2_0169-s706 [dev]
    # TEXT: 노동자들이 일할 수 있는 여건을 만들고 노동자가 주인이 된 상태에서라면 노동자보고 일하지 말라고 해도 한다.
    # TRANSLIT: no.dong.ja.deul.i il.hal su iss.neun yeo.geon.eul man.deul.go no.dong.ja.ga ju.in.i doen sang.tae.e.seo.ra.myeon no.dong.ja.bo.go il.ha.ji mal.ra.go hae.do han.da
    # ENGLISH: If conditions are created where workers can work and workers become the masters, even if you tell workers not to work, they will work.
    # CONFLICT: N1:노동자가(nsubj), N2:주인이(nsubj) under pred:'된 .doen' → default: N1(노동자가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0169-s706': [('deprel', 7, 'nsubj:outer')],

    # MH2_0169-s709 [dev]
    # TEXT: 노동자에게 주인된 자세만 요구하는 게 아니라 진짜 노동자가 기업의 주인이 되게 해야 한다.
    # TRANSLIT: no.dong.ja.e.ge ju.in.doen ja.se.man yo.gu.ha.neun ge a.ni.ra jin.jja no.dong.ja.ga gi.eob.yi ju.in.i doe.ge hae.ya han.da
    # ENGLISH: We should not only demand that workers take an ownership attitude, but truly make workers the masters of corporations.
    # CONFLICT: N1:노동자가(nsubj), N2:주인이(nsubj) under pred:'되게 .doe.ge' → default: N1(노동자가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0169-s709': [('deprel', 8, 'nsubj:outer')],

    # MH2_0169-s736 [dev]
    # TEXT: 옛날의 상식이 지금은 비상식이 되듯이 자본주의 다음 시대의 눈으로 보면 자본주의 시대의 제도가 비상식이 된다.
    # TRANSLIT: yes.nal.yi sang.sig.i ji.geum.eun bi.sang.sig.i doe.deus.i ja.bon.ju.yi da.eum si.dae.yi nun.eu.ro bo.myeon ja.bon.ju.yi si.dae.yi je.do.ga bi.sang.sig.i doen.da
    # ENGLISH: The core issue on the Korean peninsula is not military confrontation but the fundamental question of reunification.
    # CONFLICT: N1:상식이(nsubj), N2:비상식이(nsubj) under pred:'되듯이 .doe.deus.i' → default: N1(상식이)→nsubj:outer [NEEDS REVIEW]
    # CONFLICT: N1:제도가(nsubj), N2:비상식이(nsubj) under pred:'된다 .doen.da' → default: N1(제도가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0169-s736': [('deprel', 2, 'nsubj:outer'), ('deprel', 13, 'nsubj:outer')],

    # MH2_0169-s755 [dev]
    # TEXT: 노동자가 기업의 주인이 되는 경제체제가 기업의 주인이 할아버지에서 아버지로, 아버지에서 아들로, 아들에서 손자로 넘어가는 체제보다 훨씬 강할 수밖에 없다.
    # TRANSLIT: no.dong.ja.ga gi.eob.yi ju.in.i doe.neun gyeong.je.che.je.ga gi.eob.yi ju.in.i hal.a.beo.ji.e.seo a.beo.ji.ro , a.beo.ji.e.seo a.deul.ro , a.deul.e.seo son.ja.ro neom.eo.ga.neun che.je.bo.da hweol.ssin gang.hal su.bagg.e eobs.da
    # ENGLISH: An economic system where workers become the masters of corporations must inevitably be far stronger than a system where ownership passes from grandfather to father, from father to son, from son to grandson.
    # CONFLICT: N1:노동자가(nsubj), N2:주인이(nsubj) under pred:'되는 .doe.neun' → default: N1(노동자가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0169-s755': [('deprel', 1, 'nsubj:outer')],

    # MH2_0173-s103 [train]
    # TEXT: 농민운동이 반자본주의 운동이 되는 까닭은 여기에 있다.
    # TRANSLIT: nong.min.un.dong.i ban.ja.bon.ju.yi un.dong.i doe.neun gga.darg.eun yeo.gi.e iss.da
    # ENGLISH: This is why the peasant movement becomes an anti-capitalist movement.
    # CONFLICT: N1:농민운동이(nsubj), N2:운동이(csubj) under pred:'되는 .doe.neun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0173-s103': [('deprel', 1, 'nsubj:outer')],

    # MH2_0173-s207 [train]
    # TEXT: 따라서 수운의 동학사상이 농민혁명의 혁명이념이 되기 위해서는 보다 실천적이며 구체적으로, 또는 보다 사회 정치적 측면에서 새롭게 해석되고 발전되어야 하는 과제가 남아 있었다.
    # TRANSLIT: dda.ra.seo su.un.yi dong.hag.sa.sang.i nong.min.hyeog.myeong.yi hyeog.myeong.i.nyeom.i doe.gi wi.hae.seo.neun bo.da sil.cheon.jeog.i.myeo gu.che.jeog.eu.ro , ddo.neun bo.da sa.hoe jeong.chi.jeog cheug.myeon.e.seo sae.rob.ge hae.seog.doe.go bal.jeon.doe.eo.ya ha.neun gwa.je.ga nam.a iss.eoss.da
    # ENGLISH: Therefore, for Suun's Donghak thought to become the revolutionary ideology of the peasant revolution, there remained the task of being newly interpreted and developed in a more practical and concrete, or more socio-political way.
    # CONFLICT: N1:동학사상이(nsubj), N2:혁명이념이(csubj) under pred:'되기 .doe.gi' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0173-s207': [('deprel', 3, 'nsubj:outer')],

    # MH2_0173-s8 [train]
    # TEXT: 그 가치의 실현을 전제로 한 진보만이 대가, 곧 국민대중의 희생을 받는 자격이 있을 것이다.
    # TRANSLIT: geu ga.chi.yi sil.hyeon.eul jeon.je.ro han jin.bo.man.i dae.ga , god gug.min.dae.jung.yi hyi.saeng.eul bad.neun ja.gyeog.i iss.eul geos.i.da
    # ENGLISH: Only progress premised on the realization of those values deserves the sacrifice — that is, the sacrifice of the common people.
    # CONFLICT: N1:진보만이(nsubj), N2:자격이(nsubj) under pred:'있을 .iss.eul' → default: N1(진보만이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0173-s8': [('deprel', 6, 'nsubj:outer')],

    # MH2_0173-s94 [train]
    # TEXT: 이런 차이가 나타나는 까닭은 1894 년 농민전쟁은 농민운동이지 그 자체가 부르주아혁명의 모든 것이 아니라는 점을 고려하지 못한 때문으로 보인다.
    # TRANSLIT: i.reon cha.i.ga na.ta.na.neun gga.darg.eun 1894 nyeon nong.min.jeon.jaeng.eun nong.min.un.dong.i.ji geu ja.che.ga bu.reu.ju.a.hyeog.myeong.yi mo.deun geos.i a.ni.ra.neun jeom.eul go.ryeo.ha.ji mos.han ddae.mun.eu.ro bo.in.da
    # ENGLISH: The reason this difference appears seems to be because it failed to consider that the 1894 Peasant War was a peasant movement and was not in itself the totality of a bourgeois revolution.
    # CONFLICT: N1:자체가(nsubj), N2:것이(csubj) under pred:'아니라는 .a.ni.ra.neun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0173-s94': [('deprel', 10, 'nsubj:outer')],

    # MH2_0174-s256 [train]
    # TEXT: 모기의 습격, 등에의 등쌀에 온 땅이 쑥밭이 되었다.
    # TRANSLIT: mo.gi.yi seub.gyeog , deung.e.yi deung.ssal.e on ddang.i ssug.bat.i doe.eoss.da
    # ENGLISH: With the assault of mosquitoes and the torment of horseflies, the entire land became a wasteland.
    # CONFLICT: N1:땅이(nsubj), N2:쑥밭이(csubj) under pred:'되었다 .doe.eoss.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0174-s256': [('deprel', 7, 'nsubj:outer')],

    # MH2_0174-s3 [train]
    # TEXT: 그 심정이 여간 아픈 게 아니었다.
    # TRANSLIT: geu sim.jeong.i yeo.gan a.peun ge a.ni.eoss.da
    # ENGLISH: His feelings were quite painful.
    # CONFLICT: N1:심정이(nsubj), N2:게(csubj) under pred:'아니었다 .a.ni.eoss.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0174-s3': [('deprel', 2, 'nsubj:outer')],

    # MH2_0174-s315 [train]
    # TEXT: 온 세계가 나의 것이 아니냐?
    # TRANSLIT: on se.gye.ga na.yi geos.i a.ni.nya ?
    # ENGLISH: Is not all the world mine?
    # CONFLICT: N1:세계가(nsubj), N2:것이(csubj) under pred:'아니냐 .a.ni.nya' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0174-s315': [('deprel', 2, 'nsubj:outer')],

    # MH2_0174-s344 [train]
    # TEXT: 아론이 이처럼 조롱거리가 되게 하였던 것이다.
    # TRANSLIT: a.ron.i i.cheo.reom jo.rong.geo.ri.ga doe.ge ha.yeoss.deon geos.i.da
    # ENGLISH: Thus Aaron was made a laughingstock.
    # CONFLICT: N1:아론이(nsubj), N2:조롱거리가(csubj) under pred:'되게 .doe.ge' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0174-s344': [('deprel', 1, 'nsubj:outer')],

    # MH2_0174-s42 [train]
    # TEXT: 노아가 6 백 1 살이 되던 해 정월 초하루, 물은 다 빠지고 땅은 말라 있었다.
    # TRANSLIT: no.a.ga 6 baeg 1 sal.i doe.deon hae jeong.weol cho.ha.ru , mul.eun da bba.ji.go ddang.eun mal.ra iss.eoss.da
    # ENGLISH: On the first day of the first month, in the 601st year of Noah's life, the water had all receded and the ground was dry.
    # CONFLICT: N1:노아가(nsubj), N2:살이(csubj) under pred:'되던 .doe.deon' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0174-s42': [('deprel', 1, 'nsubj:outer')],

    # MH2_0174-s442 [train]
    # TEXT: 약 10 년간의 여행생활 후 헤로도토스는 기원전 444 년 아테네가 중심이 되어 기획한 남이탈리아의 드리오이시의 식민에 참가하고 있다.
    # TRANSLIT: yag 10 nyeon.gan.yi yeo.haeng.saeng.hwal hu he.ro.do.to.seu.neun gi.weon.jeon 444 nyeon a.te.ne.ga jung.sim.i doe.eo gi.hoeg.han nam.i.tal.ri.a.yi deu.ri.o.i.si.yi sig.min.e cham.ga.ha.go iss.da
    # ENGLISH: After about 10 years of travel, Herodotus in 444 BC participated in the colonization of Thurii in southern Italy, planned with Athens at the center.
    # CONFLICT: N1:아테네가(nsubj), N2:중심이(csubj) under pred:'되어 .doe.eo' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0174-s442': [('deprel', 10, 'nsubj:outer')],

    # MH2_0174-s516 [train]
    # TEXT: 의논 끝에 손을 붙잡고 히말라야 산속으로 도망가 정착한 것이 석가족이 되었고 나라를 만든 유래다.
    # TRANSLIT: yi.non ggeut.e son.eul but.jab.go hi.mal.ra.ya san.sog.eu.ro do.mang.ga jeong.chag.han geos.i seog.ga.jog.i doe.eoss.go na.ra.reul man.deun yu.rae.da
    # ENGLISH: After deliberation, they held hands and fled into the Himalayan mountains to settle, and those who settled became the Shakya clan — this is the origin of how they came to form a nation.
    # CONFLICT: N1:것이(nsubj), N2:석가족이(nsubj) under pred:'되었고 .doe.eoss.go' → default: N1(것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0174-s516': [('deprel', 9, 'nsubj:outer')],

    # MH2_0176-s53 [train]
    # TEXT: 필라델피아 내에서는 몇 마일의 거리가 전혀 문제가 되지 않았다고 한다.
    # TRANSLIT: pil.ra.del.pi.a nae.e.seo.neun myeoch ma.il.yi geo.ri.ga jeon.hyeo mun.je.ga doe.ji anh.ass.da.go han.da
    # ENGLISH: Within Philadelphia, a distance of several miles was said not to be a problem at all.
    # CONFLICT: N1:거리가(nsubj), N2:문제가(csubj) under pred:'되지 .doe.ji' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0176-s53': [('deprel', 5, 'nsubj:outer')],

    # MH2_0180-s132 [test]
    # TEXT: 현실적인 것이 보편적인 것으로 나타남으로써 보편적인 것이 사고의 진정한 주어가 되고, 그리고 사고는 자기 자신에게 되돌아오는 것이다.
    # TRANSLIT: hyeon.sil.jeog.in geos.i bo.pyeon.jeog.in geos.eu.ro na.ta.nam.eu.ro.sseo bo.pyeon.jeog.in geos.i sa.go.yi jin.jeong.han ju.eo.ga doe.go , geu.ri.go sa.go.neun ja.gi ja.sin.e.ge doe.dol.a.o.neun geos.i.da
    # ENGLISH: By the real appearing as the universal, the universal becomes the true subject of thought, and thought returns to itself.
    # CONFLICT: N1:것이(nsubj), N2:주어가(csubj) under pred:'되고 .doe.go' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0180-s132': [('deprel', 7, 'nsubj:outer')],

    # MH2_0180-s238 [test]
    # TEXT: 그러나 이 문장은 헤겔에 있어서 "최고의 것이 사고의 자기이고 자유로운 활동성이지 사고 대상이 아니라는 점은 자명하다" 라는 것을 의미한다.
    # TRANSLIT: geu.reo.na i mun.jang.eun he.gel.e iss.eo.seo " choe.go.yi geos.i sa.go.yi ja.gi.i.go ja.yu.ro.un hwal.dong.seong.i.ji sa.go dae.sang.i a.ni.ra.neun jeom.eun ja.myeong.ha.da " ra.neun geos.eul yi.mi.han.da
    # ENGLISH: However, in Hegel this sentence means: 'It is self-evident that the highest is the self of thought and free activity, not the object of thought.'
    # CONFLICT: N1:것이(nsubj), N2:대상이(csubj) under pred:'아니라는 .a.ni.ra.neun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0180-s238': [('deprel', 8, 'nsubj:outer')],

    # MH2_0180-s313 [test]
    # TEXT: 우리들이 이것이 주제라고 간파할 때 거꾸로 된 세계에 관계하는 장이 점유하고 있는 체계적 위치가 확실해진다.
    # TRANSLIT: u.ri.deul.i i.geos.i ju.je.ra.go gan.pa.hal ddae geo.ggu.ro doen se.gye.e gwan.gye.ha.neun jang.i jeom.yu.ha.go iss.neun che.gye.jeog wi.chi.ga hwag.sil.hae.jin.da
    # ENGLISH: When we grasp that this is the subject, the systematic position occupied by the chapter dealing with the inverted world becomes clear.
    # CONFLICT: N1:우리들이(nsubj), N2:이것이(nsubj) under pred:'간파할 .gan.pa.hal' → default: N1(우리들이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0180-s313': [('deprel', 1, 'nsubj:outer')],

    # MH2_0181-s102 [train]
    # TEXT: 그러나 이런 기존의 방식은 모터의 크기가 미크론 사이즈가 되면 그다지 편리한 방식이 아니며 전자력보다는 정전기 상호간의 흡인력을 이용하는 편이 유리하다.
    # TRANSLIT: geu.reo.na i.reon gi.jon.yi bang.sig.eun mo.teo.yi keu.gi.ga mi.keu.ron sa.i.jeu.ga doe.myeon geu.da.ji pyeon.ri.han bang.sig.i a.ni.myeo jeon.ja.ryeog.bo.da.neun jeong.jeon.gi sang.ho.gan.yi heub.in.ryeog.eul i.yong.ha.neun pyeon.i yu.ri.ha.da
    # ENGLISH: However, this existing method is not so convenient when the size of the motor becomes micron size, and it is advantageous to use electrostatic mutual attraction rather than electromagnetic force.
    # CONFLICT: N1:크기가(nsubj), N2:사이즈가(csubj) under pred:'되면 .doe.myeon' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0181-s102': [('deprel', 6, 'nsubj:outer')],

    # MH2_0181-s129 [train]
    # TEXT: 아마도 많은 사람들이 안경테의 소형나사가 풀어져서 곤란을 겪었던 경험이 있을 것이다.
    # TRANSLIT: a.ma.do manh.eun sa.ram.deul.i an.gyeong.te.yi so.hyeong.na.sa.ga pul.eo.jyeo.seo gon.ran.eul gyeogg.eoss.deon gyeong.heom.i iss.eul geos.i.da
    # ENGLISH: Many people have probably had the experience of being troubled by the loosening of the small screws in their eyeglass frames.
    # CONFLICT: N1:사람들이(nsubj), N2:경험이(nsubj) under pred:'있을 .iss.eul' → default: N1(사람들이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0181-s129': [('deprel', 3, 'nsubj:outer')],

    # MH2_0181-s135 [train]
    # TEXT: 지금까지 정밀기계공학의 세계에서는 주로 가공의 정도 (精度) 가 화제가 되어 왔으며 기계 부품의 미세화와 소형화는 그다지 중시되지 않았다.
    # TRANSLIT: ji.geum.gga.ji jeong.mil.gi.gye.gong.hag.yi se.gye.e.seo.neun ju.ro ga.gong.yi jeong.do ( jīngdù ) ga hwa.je.ga doe.eo wass.eu.myeo gi.gye bu.pum.yi mi.se.hwa.wa so.hyeong.hwa.neun geu.da.ji jung.si.doe.ji anh.ass.da
    # ENGLISH: Until now in the world of precision mechanical engineering, machining precision has mainly been the topic of discussion, and miniaturization and downsizing of machine parts have not been given much importance.
    # CONFLICT: N1:정도(nsubj), N2:화제가(csubj) under pred:'되어 .doe.eo' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0181-s135': [('deprel', 6, 'nsubj:outer')],

    # MH2_0181-s136 [train]
    # TEXT: 둘째, 전자부품과 달리 기계에서는 그저 작다고만 하는 것이 능사가 아니라는 것이다.
    # TRANSLIT: dul.jjae , jeon.ja.bu.pum.gwa dal.ri gi.gye.e.seo.neun geu.jeo jag.da.go.man ha.neun geos.i neung.sa.ga a.ni.ra.neun geos.i.da
    # ENGLISH: Second, unlike electronic components, it is not simply a virtue for machines to be small.
    # CONFLICT: N1:것이(nsubj), N2:능사가(csubj) under pred:'아니라는 .a.ni.ra.neun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0181-s136': [('deprel', 9, 'nsubj:outer')],

    # MH2_0181-s162 [train]
    # TEXT: 현재의 반도체 LSI의 제조기술에서는 (招請淨) 상태에서 얼마나 미세하게, 그리고 정확하게 전자회로를 묘사하는가가 기술발전의 척도가 된다.
    # TRANSLIT: hyeon.jae.yi ban.do.che LSI.yi je.jo.gi.sul.e.seo.neun ( zhāoqǐngjìng ) sang.tae.e.seo eol.ma.na mi.se.ha.ge , geu.ri.go jeong.hwag.ha.ge jeon.ja.hoe.ro.reul myo.sa.ha.neun.ga.ga gi.sul.bal.jeon.yi cheog.do.ga doen.da
    # ENGLISH: In current semiconductor LSI manufacturing technology, how finely and accurately electronic circuits are drawn in an ultra-clean state becomes the measure of technological advancement.
    # CONFLICT: N1:묘사하는가가(nsubj), N2:척도가(csubj) under pred:'된다 .doen.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0181-s162': [('deprel', 15, 'nsubj:outer')],

    # MH2_0181-s211 [train]
    # TEXT: 따라서 치수가 작아지면 상대적으로 마찰에 의한 에너지손실이 커지게 되는 것으로, 이것이 바로 마이크로머신에 있어 마찰이 문제가 되는 이유이다.
    # TRANSLIT: dda.ra.seo chi.su.ga jag.a.ji.myeon sang.dae.jeog.eu.ro ma.chal.e yi.han e.neo.ji.son.sil.i keo.ji.ge doe.neun geos.eu.ro , i.geos.i ba.ro ma.i.keu.ro.meo.sin.e iss.eo ma.chal.i mun.je.ga doe.neun i.yu.i.da
    # ENGLISH: Therefore, as dimensions decrease, energy loss due to friction relatively increases, and this is precisely why friction becomes a problem in micromachines.
    # CONFLICT: N1:마찰이(nsubj), N2:문제가(nsubj) under pred:'되는 .doe.neun' → default: N1(마찰이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0181-s211': [('deprel', 16, 'nsubj:outer')],

    # MH2_0182-s119 [train]
    # TEXT: 자연자원이 부족한 우리 나라는 독창적으로 창조된 고부가가치 기술자원이 곧 재산이 되어야 한다.
    # TRANSLIT: ja.yeon.ja.weon.i bu.jog.han u.ri na.ra.neun dog.chang.jeog.eu.ro chang.jo.doen go.bu.ga.ga.chi gi.sul.ja.weon.i god jae.san.i doe.eo.ya han.da
    # ENGLISH: Our country, lacking in natural resources, must make independently created high-value-added technological resources its wealth.
    # CONFLICT: N1:기술자원이(nsubj), N2:재산이(csubj) under pred:'되어야 .doe.eo.ya' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0182-s119': [('deprel', 8, 'nsubj:outer')],

    # MH2_0184-s170 [train]
    # TEXT: 비는 그 지역의 우신이 기쁘거나 화가 났을 때 내렸는데 이것은 환경과 지역에 따라 달랐다.
    # TRANSLIT: bi.neun geu ji.yeog.yi u.sin.i gi.bbeu.geo.na hwa.ga nass.eul ddae nae.ryeoss.neun.de i.geos.eun hwan.gyeong.gwa ji.yeog.e dda.ra dal.rass.da
    # ENGLISH: Rain fell when the local rain god was pleased or angry, and this differed according to environment and region.
    # CONFLICT: N1:우신이(nsubj), N2:화가(nsubj) under pred:'났을 .nass.eul' → default: N1(우신이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0184-s170': [('deprel', 4, 'nsubj:outer')],

    # MH2_0184-s385 [train]
    # TEXT: 헬레니즘과 로마 시대의 기능공들은 최소한 그들이 전임자들만큼 능력이 있어서 그들은 새롭고 중요한 과정과 물질을 창안했다.
    # TRANSLIT: hel.re.ni.jeum.gwa ro.ma si.dae.yi gi.neung.gong.deul.eun choe.so.han geu.deul.i jeon.im.ja.deul.man.keum neung.ryeog.i iss.eo.seo geu.deul.eun sae.rob.go jung.yo.han gwa.jeong.gwa mul.jil.eul chang.an.haess.da
    # ENGLISH: Craftsmen of the Hellenistic and Roman eras were at least as capable as their predecessors, and they invented new and important processes and materials.
    # CONFLICT: N1:그들이(nsubj), N2:능력이(nsubj) under pred:'있어서 .iss.eo.seo' → default: N1(그들이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0184-s385': [('deprel', 6, 'nsubj:outer')],

    # MH2_0185-s118 [train]
    # TEXT: 우리는 리듬이라는 것을 규칙적인 것만으로 생각하여 시에 있어서는 이른바 정형시만이 리듬이 있다고 생각하기 쉽다.
    # TRANSLIT: u.ri.neun ri.deum.i.ra.neun geos.eul gyu.chig.jeog.in geos.man.eu.ro saeng.gag.ha.yeo si.e iss.eo.seo.neun i.reun.ba jeong.hyeong.si.man.i ri.deum.i iss.da.go saeng.gag.ha.gi swib.da
    # ENGLISH: We tend to think of rhythm only as something regular, and thus easily think that in poetry only so-called formal poetry has rhythm.
    # CONFLICT: N1:정형시만이(nsubj), N2:리듬이(nsubj) under pred:'있다고 .iss.da.go' → default: N1(정형시만이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0185-s118': [('deprel', 10, 'nsubj:outer')],

    # MH2_0185-s122 [train]
    # TEXT: <청노루> 의 경우 그것이 시가 되는 데는 특히 리듬이 중요한 구실을 하고 있다.
    # TRANSLIT: < cheong.no.ru > yi gyeong.u geu.geos.i si.ga doe.neun de.neun teug.hi ri.deum.i jung.yo.han gu.sil.eul ha.go iss.da
    # ENGLISH: In the case of 'Blue Roe Deer,' rhythm plays an especially important role in it becoming a poem.
    # CONFLICT: N1:그것이(nsubj), N2:시가(csubj) under pred:'되는 .doe.neun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0185-s122': [('deprel', 6, 'nsubj:outer')],

    # MH2_0185-s140 [train]
    # TEXT: 태극기와 우리나라 사이의 유사점은 없으면서도 태극기가 우리나라를 상징하는 것은 그것이 우리나라의 국기가 되어 있기 때문이다.
    # TRANSLIT: tae.geug.gi.wa u.ri.na.ra sa.i.yi yu.sa.jeom.eun eobs.eu.myeon.seo.do tae.geug.gi.ga u.ri.na.ra.reul sang.jing.ha.neun geos.eun geu.geos.i u.ri.na.ra.yi gug.gi.ga doe.eo iss.gi ddae.mun.i.da
    # ENGLISH: Although there is no similarity between the Taegukgi and our country, the Taegukgi symbolizes our country because it has become our national flag.
    # CONFLICT: N1:그것이(nsubj), N2:국기가(csubj) under pred:'되어 .doe.eo' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0185-s140': [('deprel', 10, 'nsubj:outer')],

    # MH2_0185-s173 [train]
    # TEXT: 사색하는 기능 그것이 바로 이성 (理性) 의 바탕이 되는데, 우리는 헤아릴 수 없을 만큼 많은 생각의 싹을 가지고 있다.
    # TRANSLIT: sa.saeg.ha.neun gi.neung geu.geos.i ba.ro i.seong ( lǐxìng ) yi ba.tang.i doe.neun.de , u.ri.neun he.a.ril su eobs.eul man.keum manh.eun saeng.gag.yi ssag.eul ga.ji.go iss.da
    # ENGLISH: The thinking function — that is the very foundation of reason — and we have an incalculably large number of seeds of thought.
    # CONFLICT: N1:그것이(nsubj), N2:바탕이(nsubj) under pred:'되는데 .doe.neun.de' → default: N1(그것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0185-s173': [('deprel', 3, 'nsubj:outer')],

    # MH2_0185-s184 [train]
    # TEXT: 그러므로 이러한 자연과 사회와 예술의 전부가 우리의 생각과 느낌의 소재가 된다.
    # TRANSLIT: geu.reo.meu.ro i.reo.han ja.yeon.gwa sa.hoe.wa ye.sul.yi jeon.bu.ga u.ri.yi saeng.gag.gwa neu.ggim.yi so.jae.ga doen.da
    # ENGLISH: Therefore, all of nature, society, and art become the material of our thoughts and feelings.
    # CONFLICT: N1:전부가(nsubj), N2:소재가(csubj) under pred:'된다 .doen.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0185-s184': [('deprel', 6, 'nsubj:outer')],

    # MH2_0185-s185 [train]
    # TEXT: 바꿔 말하면 사람이 보고, 듣고, 이용하고, 만들고, 허물어 버리는 모든 것이 우리의 생각과 느낌의 재료가 된다는 말이다.
    # TRANSLIT: ba.ggweo mal.ha.myeon sa.ram.i bo.go , deud.go , i.yong.ha.go , man.deul.go , heo.mul.eo beo.ri.neun mo.deun geos.i u.ri.yi saeng.gag.gwa neu.ggim.yi jae.ryo.ga doen.da.neun mal.i.da
    # ENGLISH: In other words, everything that people see, hear, use, create, and destroy becomes the material of our thoughts and feelings.
    # CONFLICT: N1:것이(nsubj), N2:재료가(csubj) under pred:'된다는 .doen.da.neun' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0185-s185': [('deprel', 15, 'nsubj:outer')],

    # MH2_0185-s187 [train]
    # TEXT: 땅 위에 있는 모든 것이 글의 소재, 곧 재료가 된다.
    # TRANSLIT: ddang wi.e iss.neun mo.deun geos.i geul.yi so.jae , god jae.ryo.ga doen.da
    # ENGLISH: Everything on the land becomes the material — the raw material — of writing.
    # CONFLICT: N1:것이(nsubj), N2:소재(csubj) under pred:'된다 .doen.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0185-s187': [('deprel', 5, 'nsubj:outer')],

    # MH2_0185-s190 [train]
    # TEXT: 그러한 소재들이 글이 되려면 글의 표현의 과정을 거쳐야 한다.
    # TRANSLIT: geu.reo.han so.jae.deul.i geul.i doe.ryeo.myeon geul.yi pyo.hyeon.yi gwa.jeong.eul geo.chyeo.ya han.da
    # ENGLISH: For such materials to become writing, they must go through the process of written expression.
    # CONFLICT: N1:소재들이(nsubj), N2:글이(csubj) under pred:'되려면 .doe.ryeo.myeon' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0185-s190': [('deprel', 2, 'nsubj:outer')],

    # MH2_0185-s199 [train]
    # TEXT: 생각을 풀어내는 차례가 뒤범벅이 되면, 문맥이 닿지 않고 뜻이 흐려지는 글이 되기 쉽기 때문이다.
    # TRANSLIT: saeng.gag.eul pul.eo.nae.neun cha.rye.ga dwi.beom.beog.i doe.myeon , mun.maeg.i dah.ji anh.go ddeus.i heu.ryeo.ji.neun geul.i doe.gi swib.gi ddae.mun.i.da
    # ENGLISH: If the order of developing thoughts becomes jumbled, the text easily becomes one where the flow does not connect and the meaning becomes unclear.
    # CONFLICT: N1:차례가(nsubj), N2:뒤범벅이(csubj) under pred:'되면 .doe.myeon' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0185-s199': [('deprel', 3, 'nsubj:outer')],

    # MH2_0185-s203 [train]
    # TEXT: 다시 말하면, 글이란 쓰는 사람의 안에 있을 때에는 생각이 바탕이지만, 바깥에 나타날 때에는 문장이 근본이 된다.
    # TRANSLIT: da.si mal.ha.myeon , geul.i.ran sseu.neun sa.ram.yi an.e iss.eul ddae.e.neun saeng.gag.i ba.tang.i.ji.man , ba.ggat.e na.ta.nal ddae.e.neun mun.jang.i geun.bon.i doen.da
    # ENGLISH: In other words, when writing is inside the writer, thought is the foundation; but when it appears outside, the sentence becomes the essence.
    # CONFLICT: N1:문장이(nsubj), N2:근본이(csubj) under pred:'된다 .doen.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0185-s203': [('deprel', 16, 'nsubj:outer')],

    # MH2_0185-s204 [train]
    # TEXT: 그러므로 생각을 깊게 하는 것이 글 쓰는 첫 힘이 되듯이, 문장을 깔끔하게 다듬는 것이 또한 글 쓰는 마지막 힘이 된다.
    # TRANSLIT: geu.reo.meu.ro saeng.gag.eul gip.ge ha.neun geos.i geul sseu.neun cheos him.i doe.deus.i , mun.jang.eul ggal.ggeum.ha.ge da.deum.neun geos.i ddo.han geul sseu.neun ma.ji.mag him.i doen.da
    # ENGLISH: What ultimately becomes the issue in environmental ethics is not individual behavior but systemic change.
    # CONFLICT: N1:것이(nsubj), N2:힘이(csubj) under pred:'되듯이 .doe.deus.i' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    # CONFLICT: N1:것이(nsubj), N2:힘이(csubj) under pred:'된다 .doen.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0185-s204': [('deprel', 5, 'nsubj:outer'), ('deprel', 15, 'nsubj:outer')],

    # MH2_0185-s257 [train]
    # TEXT: 추리에는 그것이 올바른 것이 되게 해 주는 형식적 규칙이 있다.
    # TRANSLIT: chu.ri.e.neun geu.geos.i ol.ba.reun geos.i doe.ge hae ju.neun hyeong.sig.jeog gyu.chig.i iss.da
    # ENGLISH: In inference there are formal rules that make it correct.
    # CONFLICT: N1:그것이(nsubj), N2:것이(csubj) under pred:'되게 .doe.ge' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0185-s257': [('deprel', 2, 'nsubj:outer')],

    # MH2_0185-s27 [train]
    # TEXT: 조그만 아이가 소녀가 되고 소녀가 어엿한 처녀가 되고 어엿한 처녀는 아내가 된다.
    # TRANSLIT: jo.geu.man a.i.ga so.nyeo.ga doe.go so.nyeo.ga eo.yeos.han cheo.nyeo.ga doe.go eo.yeos.han cheo.nyeo.neun a.nae.ga doen.da
    # ENGLISH: The reason environmental ethics becomes necessary is not pollution itself but the moral relationship between humans and nature.
    # CONFLICT: N1:아이가(nsubj), N2:소녀가(csubj) under pred:'되고 .doe.go' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    # CONFLICT: N1:소녀가(nsubj), N2:처녀가(csubj) under pred:'되고 .doe.go' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0185-s27': [('deprel', 2, 'nsubj:outer'), ('deprel', 5, 'nsubj:outer')],

    # MH2_0185-s276 [train]
    # TEXT: 그런, 귀납법이 유비 추리보다 과학적인 연구 방법으로서 휠씬 쓸모가 있는 것은 이 방법에 의해 자연 법칙이 확립되기 때문이다.
    # TRANSLIT: geu.reon , gwi.nab.beob.i yu.bi chu.ri.bo.da gwa.hag.jeog.in yeon.gu bang.beob.eu.ro.seo hwil.ssin sseul.mo.ga iss.neun geos.eun i bang.beob.e yi.hae ja.yeon beob.chig.i hwag.rib.doe.gi ddae.mun.i.da
    # ENGLISH: That induction is far more useful as a scientific research method than analogical reasoning is because natural laws are established by this method.
    # CONFLICT: N1:귀납법이(nsubj), N2:쓸모가(nsubj) under pred:'있는 .iss.neun' → default: N1(귀납법이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0185-s276': [('deprel', 3, 'nsubj:outer')],

    # MH2_0185-s285 [train]
    # TEXT: 그러나, 귀납법에 의해 얻은 자연 과학의 법칙들이 수학적 지식과 같은 필연적인 지식이 아니라고 해서 그 값어치가 떨어지는 것은 아니다.
    # TRANSLIT: geu.reo.na , gwi.nab.beob.e yi.hae eod.eun ja.yeon gwa.hag.yi beob.chig.deul.i su.hag.jeog ji.sig.gwa gat.eun pil.yeon.jeog.in ji.sig.i a.ni.ra.go hae.seo geu gabs.eo.chi.ga ddeol.eo.ji.neun geos.eun a.ni.da
    # ENGLISH: However, just because the laws of natural science obtained by induction are not necessary knowledge like mathematical knowledge does not mean their value diminishes.
    # CONFLICT: N1:법칙들이(nsubj), N2:지식이(csubj) under pred:'아니라고 .a.ni.ra.go' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0185-s285': [('deprel', 8, 'nsubj:outer')],

    # MH2_0185-s286 [train]
    # TEXT: 우리가 과학의 탐구를 통해 얻은 유용한 지식은 거의 모두가 진리일 가능성이 높은 경험적 지식이다.
    # TRANSLIT: u.ri.ga gwa.hag.yi tam.gu.reul tong.hae eod.eun yu.yong.han ji.sig.eun geo.yi mo.du.ga jin.ri.il ga.neung.seong.i nop.eun gyeong.heom.jeog ji.sig.i.da
    # ENGLISH: Almost all useful knowledge obtained through scientific inquiry is empirical knowledge with a high probability of being true.
    # CONFLICT: N1:모두가(nsubj), N2:가능성이(nsubj) under pred:'높은 .nop.eun' → default: N1(모두가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0185-s286': [('deprel', 9, 'nsubj:outer')],

    # MH2_0190-s169 [test]
    # TEXT: 다만 러시아, 우크라이나, 카자흐 등 큰 공화국들로부터 우리가 필요한 자원을 수입하는 것이 경제교류의 중심이 될 것으로 보인다.
    # TRANSLIT: da.man reo.si.a , u.keu.ra.i.na , ka.ja.heu deung keun gong.hwa.gug.deul.ro.bu.teo u.ri.ga pil.yo.han ja.weon.eul su.ib.ha.neun geos.i gyeong.je.gyo.ryu.yi jung.sim.i doel geos.eu.ro bo.in.da
    # ENGLISH: The core issue of Korean unification is not political differences but the question of how to create a shared future.
    # CONFLICT: N1:것이(nsubj), N2:중심이(nsubj) under pred:'될 .doel' → default: N1(것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0190-s169': [('deprel', 14, 'nsubj:outer')],

    # MH2_0190-s224 [test]
    # TEXT: 현재는 인천항과 제일 가까운 산동성의 위해가 우리 기업이 중국에 진출하는 데 편리한 교두보가 될 것으로 꼽히기도 한다.
    # TRANSLIT: hyeon.jae.neun in.cheon.hang.gwa je.il ga.gga.un san.dong.seong.yi wi.hae.ga u.ri gi.eob.i jung.gug.e jin.chul.ha.neun de pyeon.ri.han gyo.du.bo.ga doel geos.eu.ro ggob.hi.gi.do han.da
    # ENGLISH: What ultimately becomes the issue is not the mechanism of unification but its content.
    # CONFLICT: N1:위해가(nsubj), N2:교두보가(nsubj) under pred:'될 .doel' → default: N1(위해가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0190-s224': [('deprel', 6, 'nsubj:outer')],

    # MH2_0190-s24 [test]
    # TEXT: 그 결과 만든 물건이 시장에서 날개 돋친 듯이 잘 팔리면 막대한 이윤을 얻을 수 있다.
    # TRANSLIT: geu gyeol.gwa man.deun mul.geon.i si.jang.e.seo nal.gae dod.chin deus.i jal pal.ri.myeon mag.dae.han i.yun.eul eod.eul su iss.da
    # ENGLISH: As a result, if what is produced sells like hotcakes in the market, enormous profits can be obtained.
    # CONFLICT: N1:물건이(nsubj), N2:듯이(nsubj) under pred:'팔리면 .pal.ri.myeon' → default: N1(물건이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0190-s24': [('deprel', 4, 'nsubj:outer')],

    # MH2_0190-s337 [test]
    # TEXT: 각국의 입장에서 보면 수출을 증대시키고 수입을 감소시키는 것이 실업을 줄이고 불황을 타개하는 데 도움이 될 것이다.
    # TRANSLIT: gag.gug.yi ib.jang.e.seo bo.myeon su.chul.eul jeung.dae.si.ki.go su.ib.eul gam.so.si.ki.neun geos.i sil.eob.eul jul.i.go bul.hwang.eul ta.gae.ha.neun de do.um.i doel geos.i.da
    # ENGLISH: The reason economic cooperation becomes a stepping stone to unification is that shared economic interests create shared political will.
    # CONFLICT: N1:것이(nsubj), N2:도움이(nsubj) under pred:'될 .doel' → default: N1(것이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0190-s337': [('deprel', 8, 'nsubj:outer')],

    # MH2_0190-s424 [test]
    # TEXT: 한국의 모든 산업이 국제경쟁력이 있는 산업이 되어야만 비로소 살아남을 수 있음을 국민들은 인식해야 할 것이다.
    # TRANSLIT: han.gug.yi mo.deun san.eob.i gug.je.gyeong.jaeng.ryeog.i iss.neun san.eob.i doe.eo.ya.man bi.ro.so sal.a.nam.eul su iss.eum.eul gug.min.deul.eun in.sig.hae.ya hal geos.i.da
    # ENGLISH: The reason the shipbuilding industry must become a strategic industry is that it combines both labor-intensive and technology-intensive characteristics.
    # CONFLICT: N1:산업이(nsubj), N2:산업이(csubj) under pred:'되어야만 .doe.eo.ya.man' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0190-s424': [('deprel', 3, 'nsubj:outer')],

    # MH2_0190-s46 [test]
    # TEXT: 공산주의의 실제 경험이 보여 주는 값진 교훈은 평등의 지나친 추구가 결국 엄청난 비효율을 초래하여 인민 모두가 가난해졌다는 점이다.
    # TRANSLIT: gong.san.ju.yi.yi sil.je gyeong.heom.i bo.yeo ju.neun gabs.jin gyo.hun.eun pyeong.deung.yi ji.na.chin chu.gu.ga gyeol.gug eom.cheong.nan bi.hyo.yul.eul cho.rae.ha.yeo in.min mo.du.ga ga.nan.hae.jyeoss.da.neun jeom.i.da
    # ENGLISH: The valuable lesson shown by the actual experience of communism is that the excessive pursuit of equality ultimately brought about enormous inefficiency and everyone became poor.
    # CONFLICT: N1:추구가(nsubj), N2:모두가(nsubj) under pred:'가난해졌다는 .ga.nan.hae.jyeoss.da.neun' → default: N1(추구가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0190-s46': [('deprel', 10, 'nsubj:outer')],

    # MH2_0190-s484 [test]
    # TEXT: 이렇게 볼 때 두만강 개발계획처럼 국지적으로 관련국들간의 협력을 증진하는 방안이 보다 실현가능성이 높다고 하겠다.
    # TRANSLIT: i.reoh.ge bol ddae du.man.gang gae.bal.gye.hoeg.cheo.reom gug.ji.jeog.eu.ro gwan.ryeon.gug.deul.gan.yi hyeob.ryeog.eul jeung.jin.ha.neun bang.an.i bo.da sil.hyeon.ga.neung.seong.i nop.da.go ha.gess.da
    # ENGLISH: The reason the feasibility of the plan needs to be high is that a plan that cannot be implemented is no plan at all.
    # CONFLICT: N1:방안이(nsubj), N2:실현가능성이(nsubj) under pred:'높다고 .nop.da.go' → default: N1(방안이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0190-s484': [('deprel', 10, 'nsubj:outer')],

    # MH2_0190-s53 [test]
    # TEXT: 그러나 지나친 평등의 추구가 유인제도와 상충되어 모든 인민의 생활수준이 하락했음을 공산권 국가의 경험이 보여 준다.
    # TRANSLIT: geu.reo.na ji.na.chin pyeong.deung.yi chu.gu.ga yu.in.je.do.wa sang.chung.doe.eo mo.deun in.min.yi saeng.hwal.su.jun.i ha.rag.haess.eum.eul gong.san.gweon gug.ga.yi gyeong.heom.i bo.yeo jun.da
    # ENGLISH: However, the experience of communist countries shows that the excessive pursuit of equality conflicted with the incentive system and lowered the standard of living of all people.
    # CONFLICT: N1:추구가(nsubj), N2:생활수준이(nsubj) under pred:'하락했음을 .ha.rag.haess.eum.eul' → default: N1(추구가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0190-s53': [('deprel', 4, 'nsubj:outer')],

    # MH2_0193-s55 [train]
    # TEXT: 이것이 오늘날의 유럽 여러 민족의 조상이 되었고, 일부는 남쪽 방향으로 진출해서 이락, 이란, 터키, 인도 서북쪽 변두리 땅을 점령했던 것입니다.
    # TRANSLIT: i.geos.i o.neul.nal.yi yu.reob yeo.reo min.jog.yi jo.sang.i doe.eoss.go , il.bu.neun nam.jjog bang.hyang.eu.ro jin.chul.hae.seo i.rag , i.ran , teo.ki , in.do seo.bug.jjog byeon.du.ri ddang.eul jeom.ryeong.haess.deon geos.ib.ni.da
    # ENGLISH: These became the ancestors of the various European peoples of today, and some advanced southward to occupy the peripheral lands of Iraq, Iran, Turkey, and northwestern India.
    # CONFLICT: N1:이것이(nsubj), N2:조상이(csubj) under pred:'되었고 .doe.eoss.go' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0193-s55': [('deprel', 1, 'nsubj:outer')],

    # MH2_0193-s79 [train]
    # TEXT: 찻종은 제가 찻종이 되고 싶다고 해서 찻종이 된 건 아닌 것입니다.
    # TRANSLIT: chas.jong.eun je.ga chas.jong.i doe.go sip.da.go hae.seo chas.jong.i doen geon a.nin geos.ib.ni.da
    # ENGLISH: A teacup did not become a teacup because it wanted to be a teacup.
    # CONFLICT: N1:제가(nsubj), N2:찻종이(csubj) under pred:'되고 .doe.go' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0193-s79': [('deprel', 2, 'nsubj:outer')],

    # MH2_0193-s8 [train]
    # TEXT: 그런데, 이게 또 보통 일이 아닙니다.
    # TRANSLIT: geu.reon.de , i.ge ddo bo.tong il.i a.nib.ni.da
    # ENGLISH: However, this is no ordinary matter.
    # CONFLICT: N1:이게(nsubj), N2:일이(csubj) under pred:'아닙니다 .a.nib.ni.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0193-s8': [('deprel', 3, 'nsubj:outer')],

    # MH2_0194-s117 [train]
    # TEXT: 삼을 길러 삼베 짜는 일이 일반적인 상황이 되었다.
    # TRANSLIT: sam.eul gil.reo sam.be jja.neun il.i il.ban.jeog.in sang.hwang.i doe.eoss.da
    # ENGLISH: Growing hemp and weaving hemp cloth became a common situation.
    # CONFLICT: N1:일이(nsubj), N2:상황이(csubj) under pred:'되었다 .doe.eoss.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0194-s117': [('deprel', 5, 'nsubj:outer')],

    # MH2_0194-s438 [train]
    # TEXT: 고대국가 초기에는 모든 남자 장정 (壯丁) 이 병사가 되었던 것은 아니었다.
    # TRANSLIT: go.dae.gug.ga cho.gi.e.neun mo.deun nam.ja jang.jeong ( zhuàngdīng ) i byeong.sa.ga doe.eoss.deon geos.eun a.ni.eoss.da
    # ENGLISH: In the early stages of the ancient state, not all adult male conscripts became soldiers.
    # CONFLICT: N1:장정(nsubj), N2:병사가(csubj) under pred:'되었던 .doe.eoss.deon' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0194-s438': [('deprel', 5, 'nsubj:outer')],

    # MH2_0195-s105 [train]
    # TEXT: 이 같은 훼손의 배경에는 비석 그 자체가 오랫동안 자연 상태에 방치되어 온 까닭에 비바람에 의한 자연 마모가 그 첫째 이유가 되겠다.
    # TRANSLIT: i gat.eun hwe.son.yi bae.gyeong.e.neun bi.seog geu ja.che.ga o.raes.dong.an ja.yeon sang.tae.e bang.chi.doe.eo on gga.darg.e bi.ba.ram.e yi.han ja.yeon ma.mo.ga geu cheos.jjae i.yu.ga doe.gess.da
    # ENGLISH: The primary reason for such deterioration would be natural erosion by wind and rain, as the stele itself has been left in a natural state for a long time.
    # CONFLICT: N1:마모가(nsubj), N2:이유가(csubj) under pred:'되겠다 .doe.gess.da' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0195-s105': [('deprel', 17, 'nsubj:outer')],

    # MH2_0195-s140 [train]
    # TEXT: 더구나 당시 철의 문화 수준 (군사력, 국력) 이 왜보다 백제측이 훨씬 우월했던 점을 감안한다면 위의 해석에 도움이 되리라 본다.
    # TRANSLIT: deo.gu.na dang.si cheol.yi mun.hwa su.jun ( gun.sa.ryeog , gug.ryeog ) i wae.bo.da baeg.je.cheug.i hweol.ssin u.weol.haess.deon jeom.eul gam.an.han.da.myeon wi.yi hae.seog.e do.um.i doe.ri.ra bon.da
    # ENGLISH: Moreover, if we consider that the level of iron culture (military power, national power) at the time was far superior on the Baekje side than on the Japanese side, it seems to provide support for the above interpretation.
    # CONFLICT: N1:수준(nsubj), N2:백제측이(nsubj) under pred:'우월했던 .u.weol.haess.deon' → default: N1(수준)→nsubj:outer [NEEDS REVIEW]
    'MH2_0195-s140': [('deprel', 5, 'nsubj:outer')],

    # MH2_0195-s143 [train]
    # TEXT: 그렇기 때문에 당시의 작위 명칭에는 큰 의미를 부여하지 않는 것이 오늘날 학자들의 상식이 아닌가?
    # TRANSLIT: geu.reoh.gi ddae.mun.e dang.si.yi jag.wi myeong.ching.e.neun keun yi.mi.reul bu.yeo.ha.ji anh.neun geos.i o.neul.nal hag.ja.deul.yi sang.sig.i a.nin.ga ?
    # ENGLISH: Therefore, is it not the common sense of today's scholars not to attach much significance to the titles and ranks of that time?
    # CONFLICT: N1:것이(nsubj), N2:상식이(csubj) under pred:'아닌가 .a.nin.ga' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0195-s143': [('deprel', 10, 'nsubj:outer')],

    # MH2_0195-s186 [train]
    # TEXT: 아스카 문화에 기여한 남북조인들은 구체적으로 누구였으며, 백제와 고구려인들이 어째서 대륙에서 온 도래인이 될 수 있다는 말인가?
    # TRANSLIT: a.seu.ka mun.hwa.e gi.yeo.han nam.bug.jo.in.deul.eun gu.che.jeog.eu.ro nu.gu.yeoss.eu.myeo , baeg.je.wa go.gu.ryeo.in.deul.i eo.jjae.seo dae.ryug.e.seo on do.rae.in.i doel su iss.da.neun mal.in.ga ?
    # ENGLISH: Who specifically were the people from the Northern and Southern dynasties who contributed to Asuka culture, and why can the Baekje and Goguryeo people be described as immigrants who came from the continent?
    # CONFLICT: N1:백제와(nsubj), N2:도래인이(nsubj) under pred:'될 .doel' → default: N1(백제와)→nsubj:outer [NEEDS REVIEW]
    'MH2_0195-s186': [('deprel', 8, 'nsubj:outer')],

    # MH2_0195-s224 [train]
    # TEXT: 아스카 문화가 열도에서 자생한 문화가 아닌 이상 그 문화적 성격에 국제성을 부여하는 데는 별 무리가 없을 것이다.
    # TRANSLIT: a.seu.ka mun.hwa.ga yeol.do.e.seo ja.saeng.han mun.hwa.ga a.nin i.sang geu mun.hwa.jeog seong.gyeog.e gug.je.seong.eul bu.yeo.ha.neun de.neun byeol mu.ri.ga eobs.eul geos.i.da
    # ENGLISH: As long as Asuka culture was not a culture that arose spontaneously in the islands, there would be little difficulty in attributing international character to its cultural nature.
    # CONFLICT: N1:문화가(nsubj), N2:문화가(csubj) under pred:'아닌 .a.nin' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0195-s224': [('deprel', 2, 'nsubj:outer')],

    # MH2_0204-s124 [train]
    # TEXT: 예를 들면 극히 정확한 수성에 대한 관측으로부터, 수성의 운동이 뉴턴의 중력 이론과 미소한 차이가 있음이 알려졌다.
    # TRANSLIT: ye.reul deul.myeon geug.hi jeong.hwag.han su.seong.e dae.han gwan.cheug.eu.ro.bu.teo , su.seong.yi un.dong.i nyu.teon.yi jung.ryeog i.ron.gwa mi.so.han cha.i.ga iss.eum.i al.ryeo.jyeoss.da
    # ENGLISH: From extremely precise observations of Mercury, it became known that Mercury's motion has a slight discrepancy with Newton's gravitational theory.
    # CONFLICT: N1:운동이(nsubj), N2:차이가(nsubj) under pred:'있음이 .iss.eum.i' → default: N1(운동이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0204-s124': [('deprel', 10, 'nsubj:outer')],

    # MH2_0204-s202 [train]
    # TEXT: 왜냐하면 공이 두 번 튕기는 동안 (1 초) 에 기차가 그만큼 달렸기 때문이다.
    # TRANSLIT: wae.nya.ha.myeon gong.i du beon twing.gi.neun dong.an ( 1 cho ) e gi.cha.ga geu.man.keum dal.ryeoss.gi ddae.mun.i.da
    # ENGLISH: This is because the train traveled that distance while the ball bounced twice (1 second).
    # CONFLICT: N1:공이(nsubj), N2:기차가(nsubj) under pred:'달렸기 .dal.ryeoss.gi' → default: N1(공이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0204-s202': [('deprel', 2, 'nsubj:outer')],

    # MH2_0204-s218 [train]
    # TEXT: 그는 이것이 목성의 달에서 오는 빛이 우리에게로 오는 데 시간이 더 걸리기 때문이라고 설명했다.
    # TRANSLIT: geu.neun i.geos.i mog.seong.yi dal.e.seo o.neun bich.i u.ri.e.ge.ro o.neun de si.gan.i deo geol.ri.gi ddae.mun.i.ra.go seol.myeong.haess.da
    # ENGLISH: He explained that this was because it took more time for light coming from Jupiter's moons to reach us.
    # CONFLICT: N1:이것이(nsubj), N2:빛이(nsubj), N3:시간이(nsubj) under pred:'걸리기 .geol.ri.gi' → 3-way default: N1,N2→nsubj:outer [NEEDS REVIEW]
    'MH2_0204-s218': [('deprel', 2, 'nsubj:outer'), ('deprel', 6, 'nsubj:outer')],

    # MH2_0204-s38 [train]
    # TEXT: 달에 걸리는 지구의 그림자는 언제나 둥글기 때문에 지구가 구형이 아닐 수 없다고 하였다.
    # TRANSLIT: dal.e geol.ri.neun ji.gu.yi geu.rim.ja.neun eon.je.na dung.geul.gi ddae.mun.e ji.gu.ga gu.hyeong.i a.nil su eobs.da.go ha.yeoss.da
    # ENGLISH: He argued that the Earth's shadow cast on the Moon is always round, so the Earth must be spherical.
    # CONFLICT: N1:지구가(nsubj), N2:구형이(csubj) under pred:'아닐 .a.nil' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0204-s38': [('deprel', 8, 'nsubj:outer')],

    # MH2_0204-s389 [train]
    # TEXT: 우주가 모든 방향에서 같은 모습으로 보인다는 가정이 사실이 아님은 명백하다.
    # TRANSLIT: u.ju.ga mo.deun bang.hyang.e.seo gat.eun mo.seub.eu.ro bo.in.da.neun ga.jeong.i sa.sil.i a.nim.eun myeong.baeg.ha.da
    # ENGLISH: It is clear that the assumption that the universe looks the same from all directions is not true.
    # CONFLICT: N1:가정이(nsubj), N2:사실이(nsubj) under pred:'아님은 .a.nim.eun' → default: N1(가정이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0204-s389': [('deprel', 7, 'nsubj:outer')],

    # MH2_0204-s96 [train]
    # TEXT: 허블의 관측은 우주가 대폭발로 불리는 무한히 작고 조밀 (稠密) 했던 시기가 있었음을 암시하고 있다.
    # TRANSLIT: heo.beul.yi gwan.cheug.eun u.ju.ga dae.pog.bal.ro bul.ri.neun mu.han.hi jag.go jo.mil ( chóumì ) haess.deon si.gi.ga iss.eoss.eum.eul am.si.ha.go iss.da
    # ENGLISH: Hubble's observations suggest that the universe had a period of being infinitely small and dense, called the Big Bang.
    # CONFLICT: N1:우주가(nsubj), N2:시기가(nsubj) under pred:'있었음을 .iss.eoss.eum.eul' → default: N1(우주가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0204-s96': [('deprel', 3, 'nsubj:outer')],

    # MH2_0209-s9 [dev]
    # TEXT: 바니와 클라이드가 기총소사로 온 몸이 벌집이 된 채 살해되는 장면을 느린 동작으로 잡은 마지막 장면은 당시 대단한 화제거리로 등장하였다.
    # TRANSLIT: ba.ni.wa keul.ra.i.deu.ga gi.chong.so.sa.ro on mom.i beol.jib.i doen chae sal.hae.doe.neun jang.myeon.eul neu.rin dong.jag.eu.ro jab.eun ma.ji.mag jang.myeon.eun dang.si dae.dan.han hwa.je.geo.ri.ro deung.jang.ha.yeoss.da
    # ENGLISH: The final scene, captured in slow motion, of Bonnie and Clyde being shot full of holes by machine gun fire became a huge talking point at the time.
    # CONFLICT: N1:몸이(nsubj), N2:벌집이(csubj) under pred:'된 .doen' → nsubj+csubj: nsubj→nsubj:outer (outer entity in copular construction)
    'MH2_0209-s9': [('deprel', 5, 'nsubj:outer')],

    # MH2_0285-s140 [train]
    # TEXT: 지극히 개인적인 나의 어린 시절을 회상하는 일이 가이아를 이해하는 데에 무슨 관계가 있느냐고 반문할지 모르겠다.
    # TRANSLIT: ji.geug.hi gae.in.jeog.in na.yi eo.rin si.jeol.eul hoe.sang.ha.neun il.i ga.i.a.reul i.hae.ha.neun de.e mu.seun gwan.gye.ga iss.neu.nya.go ban.mun.hal.ji mo.reu.gess.da
    # ENGLISH: One might ask what relevance recalling my extremely personal childhood has to understanding Gaia.
    # CONFLICT: N1:일이(nsubj), N2:관계가(nsubj) under pred:'있느냐고 .iss.neu.nya.go' → default: N1(일이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0285-s140': [('deprel', 7, 'nsubj:outer')],

    # MH2_0285-s406 [train]
    # TEXT: 첫번째 여름이 미처 지나기도 전에 짙은색의 꽃을 갖는 데이지들이 그렇지 못한 데이지들보다 성장이 유리했을 것은 물론이다.
    # TRANSLIT: cheos.beon.jjae yeo.reum.i mi.cheo ji.na.gi.do jeon.e jit.eun.saeg.yi ggoch.eul gaj.neun de.i.ji.deul.i geu.reoh.ji mos.han de.i.ji.deul.bo.da seong.jang.i yu.ri.haess.eul geos.eun mul.ron.i.da
    # ENGLISH: Before the first summer had even passed, it would of course have been advantageous for dark-colored daisies to grow compared to those that were not.
    # CONFLICT: N1:데이지들이(nsubj), N2:성장이(nsubj) under pred:'유리했을 .yu.ri.haess.eul' → default: N1(데이지들이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0285-s406': [('deprel', 9, 'nsubj:outer')],

    # MH2_0285-s479 [train]
    # TEXT: 도대체 이러한 이론이 무슨 쓸모가 있겠는가?
    # TRANSLIT: do.dae.che i.reo.han i.ron.i mu.seun sseul.mo.ga iss.gess.neun.ga ?
    # ENGLISH: What use could such a theory possibly be?
    # CONFLICT: N1:이론이(nsubj), N2:쓸모가(nsubj) under pred:'있겠는가 .iss.gess.neun.ga' → default: N1(이론이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0285-s479': [('deprel', 3, 'nsubj:outer')],

    # MH2_0285-s495 [train]
    # TEXT: 식물이 미래에 대한 어떤 투시력이나 사전 계획이나 예비 목적이 없었음에도 불구하고 주위 기온을 조절하는 것이 가능하다는 사실이 입증된 것이다.
    # TRANSLIT: sig.mul.i mi.rae.e dae.han eo.ddeon tu.si.ryeog.i.na sa.jeon gye.hoeg.i.na ye.bi mog.jeog.i eobs.eoss.eum.e.do bul.gu.ha.go ju.wi gi.on.eul jo.jeol.ha.neun geos.i ga.neung.ha.da.neun sa.sil.i ib.jeung.doen geos.i.da
    # ENGLISH: It has been proven that plants can regulate the surrounding temperature even without any clairvoyance, advance planning, or preparatory purpose regarding the future.
    # CONFLICT: N1:식물이(nsubj), N2:것이(nsubj) under pred:'가능하다는 .ga.neung.ha.da.neun' → default: N1(식물이)→nsubj:outer [NEEDS REVIEW]
    'MH2_0285-s495': [('deprel', 1, 'nsubj:outer')],

    # MH2_0286-s16 [train]
    # TEXT: 게다가 방송국이란 데가 선후배간의 법도가 엄격하여 아니꼽고 더러운 일이 있어도 남녀를 불문코 견습 아나운서들은 그녀 앞에서 쩔쩔맸다.
    # TRANSLIT: ge.da.ga bang.song.gug.i.ran de.ga seon.hu.bae.gan.yi beob.do.ga eom.gyeog.ha.yeo a.ni.ggob.go deo.reo.un il.i iss.eo.do nam.nyeo.reul bul.mun.ko gyeon.seub a.na.un.seo.deul.eun geu.nyeo ap.e.seo jjeol.jjeol.maess.da
    # ENGLISH: Furthermore, broadcasting stations are places where the hierarchy between senior and junior is strict, so even if there were unpleasant and dirty things, trainee announcers regardless of gender had to bow and scrape before her.
    # CONFLICT: N1:데가(nsubj), N2:법도가(nsubj) under pred:'엄격하여 .eom.gyeog.ha.yeo' → default: N1(데가)→nsubj:outer [NEEDS REVIEW]
    'MH2_0286-s16': [('deprel', 3, 'nsubj:outer')],

    # MH2_0286-s289 [train]
    # TEXT: 나이가 28 세 동갑이라는 것 말고는 방송 경력도, 사회적 활동, 교우 관계 등 모든 게 그녀가 앞서 있었다.
    # TRANSLIT: na.i.ga 28 se dong.gab.i.ra.neun geos mal.go.neun bang.song gyeong.ryeog.do , sa.hoe.jeog hwal.dong , gyo.u gwan.gye deung mo.deun ge geu.nyeo.ga ap.seo iss.eoss.da
    # ENGLISH: Apart from both being 28 years old, she was ahead in everything — broadcasting career, social activities, personal relationships, and so on.
    # CONFLICT: N1:게(nsubj), N2:그녀가(nsubj) under pred:'앞서 .ap.seo' → default: N1(게)→nsubj:outer [NEEDS REVIEW]
    'MH2_0286-s289': [('deprel', 17, 'nsubj:outer')],

}


def apply_fixes(doc, fixes):
    fixed = 0
    for bundle in doc.bundles:
        for tree in bundle.trees:
            sid = tree.sent_id
            if sid not in fixes:
                continue
            nodes = {n.ord: n for n in tree.descendants}
            for op in fixes[sid]:
                if op[0] == 'deprel':
                    _, nid, new_deprel = op
                    if nid in nodes:
                        nodes[nid].deprel = new_deprel
                elif op[0] == 'reparent':
                    _, nid, new_head_id, new_deprel = op
                    if nid in nodes and new_head_id in nodes:
                        nodes[nid].parent = nodes[new_head_id]
                        nodes[nid].deprel = new_deprel
            fixed += 1
    return fixed


if __name__ == '__main__':
    base = '.'
    splits = {
        'train': os.path.join(base, 'ko_kaist-ud-train.conllu'),
        'dev':   os.path.join(base, 'ko_kaist-ud-dev.conllu'),
        'test':  os.path.join(base, 'ko_kaist-ud-test.conllu'),
    }
    for split, path in splits.items():
        doc = udapi.Document(path)
        n = apply_fixes(doc, FIXES)
        doc.store_conllu(path)
        print(f"Fixed {n} sentences in {split} split ({path})")
