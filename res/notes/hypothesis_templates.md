Talks about {topic}.
Is discussing {subject}.
Is referring to {concept}.
The conversation revolves around {issue}.
The actors of the conversation are talking about {theme}.
The main topic of discussion is {area}.
The focus is on {aspect}.
The discourse centers around {subject matter}.
The main point of interest is {topic}.
The discussion is about {issue} and its implications for {context}.

# Model: MoritzLaurer/DeBERTa-v3-base-mnli
## Results
{'The topic of this article is {}.': 0.35, 'This article is about {}.': 0.465, 'This example is about {}.': 0.605, 'This text is about {}.': 0.54, 'The main subject of this text is {}.': 0.315, 'The focus of this writing is on {}.': 0.34, 'The primary topic of discussion in this text is {}.': 0.215, 'This article discusses {}.': 0.67, 'The main idea presented in this text is {}.': 0.325, 'The primary subject matter of this article is {}.': 0.25, 'The subject of this article is {}.': 0.35, 'This text covers the topic of {}.': 0.71, 'This article examines {}.': 0.595, 'The main focus of this text is {}.': 0.255, 'This article presents information on {}.': 0.635, 'The main topic covered in this text is {}.': 0.265, 'The central theme of this article is {}.': 0.275, 'This text provides insights into {}.': 0.565, 'The primary objective of this article is to discuss {}.': 0.155, 'This text examines the topic of {} in depth.': 0.33, 'The topic of this text is {}.': 0.41, 'This article delves into the topic of {}.': 0.6}
Best template: This text covers the topic of {}.
Best accuracy: 0.71



# Model: facebook /bart-large-mnli                                                                                                                                
## Results
{'The topic of this article is {}.': 0.6, 'This article is about {}.': 0.546, 'This example is about {}.': 0.502, 'This text is about {}.': 0.487, 'The main subject of this text is {}.': 0.401, 'The focus of this writing is on {}.': 0.231, 'The primary topic of discussion in this text is {}.': 0.16, 'This article discusses {}.': 0.874, 'The main idea presented in this text is {}.': 0.595, 'The primary subject matter of this article is {}.': 0.234, 'The subject of this article is {}.': 0.642, 'This text covers the topic of {}.': 0.784, 'This article examines {}.': 0.824, 'The main focus of this text is {}.': 0.215, 'This article presents information on {}.': 0.941, 'The main topic covered in this text is {}.': 0.343, 'The central theme of this article is {}.': 0.747, 'This text provides insights into {}.': 0.926, 'The primary objective of this article is to discuss {}.': 0.004, 'This text examines the topic of {} in depth.': 0.697, 'The topic of this text is {}.': 0.526, 'This article delves into the topic of {}.': 0.893}
Best template: This article presents information on {}.
Best accuracy: 0.941

{'This text examines the topic of {} in depth.': {'precision': 0.1291370034086484, 'recall': 0.66, 'f1': 0.21600918948562356}, 'The subject of this article is {}.': {'precision': 0.24160069444444443, 'recall': 0.54, 'f1': 0.3338389434076259}, 'This text covers the topic of {}.': {'precision': 0.1663488567649281, 'recall': 0.77, 'f1': 0.2735916614487874}, 'This example is about {}.': {'precision': 0.189725, 'recall': 0.4, 'f1': 0.25737419983890797}}
Best template: The subject of this article is {}.


# Model: MoritzLaurer/DeBERTa-v3-base-mnli
## Results
{'The topic of this article is {}.': {'precision': 0.14250963718820858, 'recall': 0.28, 'f1': 0.18888420476394288}, 'This article is about {}.': {'precision': 0.13733741496598642, 'recall': 0.39, 'f1': 0.20313973678575212}, 'This example is about {}.': {'precision': 0.22083160430838997, 'recall': 0.57, 'f1': 0.3183332931310036}, 'This text is about {}.': {'precision': 0.15222315656816932, 'recall': 0.49, 'f1': 0.2322848248480608}, 'The main subject of this text is {}.': {'precision': 0.13487499999999997, 'recall': 0.25, 'f1': 0.1752192270217603}, 'The focus of this writing is on {}.': {'precision': 0.14362184215896334, 'recall': 0.26, 'f1': 0.1850329940599386}, 'The primary topic of discussion in this text is {}.': {'precision': 0.08764250493096647, 'recall': 0.17, 'f1': 0.11565813523088082}, 'This article discusses {}.': {'precision': 0.18057022549760646, 'recall': 0.62, 'f1': 0.279684495483028}, 'The main idea presented in this text is {}.': {'precision': 0.11597306048652202, 'recall': 0.26, 'f1': 0.1603997674060834}, 'The primary subject matter of this article is {}.': {'precision': 0.10028741496598638, 'recall': 0.19, 'f1': 0.1312809847148908}, 'The subject of this article is {}.': {'precision': 0.14297067901234567, 'recall': 0.28, 'f1': 0.18928872430085558}, 'This text covers the topic of {}.': {'precision': 0.18200113299949605, 'recall': 0.66, 'f1': 0.28532205735105415}, 'This article examines {}.': {'precision': 0.1766608979924997, 'recall': 0.56, 'f1': 0.2685906178688124}, 'The main focus of this text is {}.': {'precision': 0.12401666666666664, 'recall': 0.22, 'f1': 0.1586182839978683}, 'This article presents information on {}.': {'precision': 0.15683134234792784, 'recall': 0.57, 'f1': 0.24598241690993783}, 'The main topic covered in this text is {}.': {'precision': 0.12488818394331214, 'recall': 0.24, 'f1': 0.16428684438327248}, 'The central theme of this article is {}.': {'precision': 0.10760069444444444, 'recall': 0.21, 'f1': 0.14229279865309558}, 'This text provides insights into {}.': {'precision': 0.11491998737490478, 'recall': 0.52, 'f1': 0.18823913130227105}, 'The primary objective of this article is to discuss {}.': {'precision': 0.038912015121630505, 'recall': 0.12, 'f1': 0.05876763706031532}, 'This text examines the topic of {} in depth.': {'precision': 0.051602307049602746, 'recall': 0.27, 'f1': 0.08664504325986584}, 'The topic of this text is {}.': {'precision': 0.13989567901234568, 'recall': 0.32, 'f1': 0.19468161727498587}, 'This article delves into the topic of {}.': {'precision': 0.18708471502817162, 'recall': 0.54, 'f1': 0.27789264174339945}}
Best template: This example is about {}.

# Model: MoritzLaurer/DeBERTa-v3-large-mnli
## Results
{'This text examines the topic of {} in depth.': {'precision': 0.19995559695335127, 'recall': 0.81, 'f1': 0.3207349590829496}, 'The subject of this article is {}.': {'precision': 0.23775565476190466, 'recall': 0.85, 'f1': 0.37157666000247874}, 'This text covers the topic of {}.': {'precision': 0.10783363462358415, 'recall': 0.95, 'f1': 0.19368254050431574}, 'This example is about {}.': {'precision': 0.164619935192473, 'recall': 0.89, 'f1': 0.277847473639045}}
Best template: The subject of this article is {}.



{
     "facebook/bart-large-mnli": {
          "The topic of this article is {}.": {
               "precision": 0.2548611111111111,
               "recall": 0.7,
               "f1": 0.3736727272727272
          },
          "This article is about {}.": {
               "precision": 0.24775,
               "recall": 0.9,
               "f1": 0.38854280113265083
          },
          "This example is about {}.": {
               "precision": 0.279,
               "recall": 0.6,
               "f1": 0.3808873720136519
          },
          "This text is about {}.": {
               "precision": 0.2678888888888889,
               "recall": 0.7,
               "f1": 0.38748708529445536
          },
          "The main subject of this text is {}.": {
               "precision": 0.15625,
               "recall": 0.4,
               "f1": 0.2247191011235955
          },
          "The focus of this writing is on {}.": {
               "precision": 0.05625,
               "recall": 0.3,
               "f1": 0.09473684210526316
          },
          "The primary topic of discussion in this text is {}.": {
               "precision": 0.10625,
               "recall": 0.2,
               "f1": 0.13877551020408163
          },
          "This article discusses {}.": {
               "precision": 0.032198202390843075,
               "recall": 0.9,
               "f1": 0.06217214767725757
          },
          "The main idea presented in this text is {}.": {
               "precision": 0.1454435941043084,
               "recall": 0.8,
               "f1": 0.24613816415706677
          },
          "The primary subject matter of this article is {}.": {
               "precision": 0.23125,
               "recall": 0.4,
               "f1": 0.29306930693069305
          },
          "The subject of this article is {}.": {
               "precision": 0.1847222222222222,
               "recall": 0.7,
               "f1": 0.29230769230769227
          },
          "This text covers the topic of {}.": {
               "precision": 0.06662414965986393,
               "recall": 0.9,
               "f1": 0.1240642181658236
          },
          "This article examines {}.": {
               "precision": 0.044881094104308385,
               "recall": 0.9,
               "f1": 0.08549855626472813
          },
          "The main focus of this text is {}.": {
               "precision": 0.15625,
               "recall": 0.4,
               "f1": 0.2247191011235955
          },
          "This article presents information on {}.": {
               "precision": 0.022585049760644994,
               "recall": 0.9,
               "f1": 0.0440643272722748
          },
          "The main topic covered in this text is {}.": {
               "precision": 0.25625,
               "recall": 0.5,
               "f1": 0.33884297520661155
          },
          "The central theme of this article is {}.": {
               "precision": 0.04199311294765838,
               "recall": 0.9,
               "f1": 0.08024220375588362
          },
          "This text provides insights into {}.": {
               "precision": 0.019476830508756916,
               "recall": 0.9,
               "f1": 0.03812852456147731
          },
          "This text examines the topic of {} in depth.": {
               "precision": 0.04090647833207357,
               "recall": 0.7,
               "f1": 0.07729594940757835
          },
          "The topic of this text is {}.": {
               "precision": 0.27847222222222223,
               "recall": 0.7,
               "f1": 0.39843860894251243
          },
          "This article delves into the topic of {}.": {
               "precision": 0.05829776077097505,
               "recall": 0.9,
               "f1": 0.10950246748289533
          }
     },
     "MoritzLaurer/DeBERTa-v3-base-mnli": {
          "The topic of this article is {}.": {
               "precision": 0.1423611111111111,
               "recall": 0.4,
               "f1": 0.20998719590268888
          },
          "This article is about {}.": {
               "precision": 0.04705555555555555,
               "recall": 0.6,
               "f1": 0.08726710740963338
          },
          "This example is about {}.": {
               "precision": 0.0761797052154195,
               "recall": 0.7,
               "f1": 0.13740579222177346
          },
          "This text is about {}.": {
               "precision": 0.036068594104308384,
               "recall": 0.6,
               "f1": 0.06804661215213564
          },
          "The main subject of this text is {}.": {
               "precision": 0.20625,
               "recall": 0.3,
               "f1": 0.24444444444444444
          },
          "The focus of this writing is on {}.": {
               "precision": 0.23125,
               "recall": 0.4,
               "f1": 0.29306930693069305
          },
          "The primary topic of discussion in this text is {}.": {
               "precision": 0.20625,
               "recall": 0.3,
               "f1": 0.24444444444444444
          },
          "This article discusses {}.": {
               "precision": 0.07380555555555554,
               "recall": 0.8,
               "f1": 0.135143211367899
          },
          "The main idea presented in this text is {}.": {
               "precision": 0.2423611111111111,
               "recall": 0.5,
               "f1": 0.32647333956969127
          },
          "The primary subject matter of this article is {}.": {
               "precision": 0.20625,
               "recall": 0.3,
               "f1": 0.24444444444444444
          },
          "The subject of this article is {}.": {
               "precision": 0.13611111111111113,
               "recall": 0.3,
               "f1": 0.1872611464968153
          },
          "This text covers the topic of {}.": {
               "precision": 0.043462726757369605,
               "recall": 0.8,
               "f1": 0.08244627842552589
          },
          "This article examines {}.": {
               "precision": 0.028833333333333322,
               "recall": 0.6,
               "f1": 0.055022528491916224
          },
          "The main focus of this text is {}.": {
               "precision": 0.13125,
               "recall": 0.3,
               "f1": 0.1826086956521739
          },
          "This article presents information on {}.": {
               "precision": 0.030874149659863938,
               "recall": 0.7,
               "f1": 0.059139880024386034
          },
          "The main topic covered in this text is {}.": {
               "precision": 0.21736111111111112,
               "recall": 0.4,
               "f1": 0.2816647919010124
          },
          "The central theme of this article is {}.": {
               "precision": 0.2125,
               "recall": 0.4,
               "f1": 0.27755102040816326
          },
          "This text provides insights into {}.": {
               "precision": 0.008463077128999746,
               "recall": 0.7,
               "f1": 0.016723959742001145
          },
          "This text examines the topic of {} in depth.": {
               "precision": 0.02894933708777629,
               "recall": 0.4,
               "f1": 0.053991153891168944
          },
          "The topic of this text is {}.": {
               "precision": 0.179,
               "recall": 0.5,
               "f1": 0.2636229749631811
          },
          "This article delves into the topic of {}.": {
               "precision": 0.05547837371863344,
               "recall": 0.7,
               "f1": 0.10280866522198256
          }
     },
     "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli": {
          "The topic of this article is {}.": {
               "precision": 0.24722222222222223,
               "recall": 0.8,
               "f1": 0.3777188328912467
          },
          "This article is about {}.": {
               "precision": 0.23463718820861676,
               "recall": 0.9,
               "f1": 0.37223082687984005
          },
          "This example is about {}.": {
               "precision": 0.16979166666666667,
               "recall": 0.8,
               "f1": 0.28012889366272825
          },
          "This text is about {}.": {
               "precision": 0.15883093978332072,
               "recall": 0.9,
               "f1": 0.27001070791195714
          },
          "The main subject of this text is {}.": {
               "precision": 0.22014583333333332,
               "recall": 0.8,
               "f1": 0.3452774317397431
          },
          "The focus of this writing is on {}.": {
               "precision": 0.17148526077097506,
               "recall": 0.8,
               "f1": 0.28242983019198226
          },
          "The primary topic of discussion in this text is {}.": {
               "precision": 0.22475524376417236,
               "recall": 0.8,
               "f1": 0.3509212489625793
          },
          "This article discusses {}.": {
               "precision": 0.22391187956664144,
               "recall": 0.8,
               "f1": 0.34989242185397357
          },
          "The main idea presented in this text is {}.": {
               "precision": 0.21413479465860416,
               "recall": 0.8,
               "f1": 0.3378403672355054
          },
          "The primary subject matter of this article is {}.": {
               "precision": 0.13804012345679012,
               "recall": 0.8,
               "f1": 0.23545282553261496
          },
          "The subject of this article is {}.": {
               "precision": 0.24770748299319725,
               "recall": 0.8,
               "f1": 0.3782849499717556
          },
          "This text covers the topic of {}.": {
               "precision": 0.2231550925925926,
               "recall": 0.9,
               "f1": 0.3576346395220145
          },
          "This article examines {}.": {
               "precision": 0.1515199829931973,
               "recall": 0.8,
               "f1": 0.2547839006244485
          },
          "The main focus of this text is {}.": {
               "precision": 0.14633093978332073,
               "recall": 0.8,
               "f1": 0.24740763913617922
          },
          "This article presents information on {}.": {
               "precision": 0.2208719135802469,
               "recall": 0.9,
               "f1": 0.35469658899253087
          },
          "The main topic covered in this text is {}.": {
               "precision": 0.2254922052154195,
               "recall": 0.8,
               "f1": 0.35181888902693564
          },
          "The central theme of this article is {}.": {
               "precision": 0.22726388888888888,
               "recall": 0.8,
               "f1": 0.353971580384787
          },
          "This text provides insights into {}.": {
               "precision": 0.21699596316181813,
               "recall": 1.0,
               "f1": 0.3566091749360474
          },
          "This text examines the topic of {} in depth.": {
               "precision": 0.1469907193976458,
               "recall": 0.8,
               "f1": 0.2483500062026246
          },
          "The topic of this text is {}.": {
               "precision": 0.2223958333333333,
               "recall": 0.8,
               "f1": 0.3480387162506367
          },
          "This article delves into the topic of {}.": {
               "precision": 0.14839104623330815,
               "recall": 1.0,
               "f1": 0.2584329557776104
          }
     }
}


# 1000 samples, 3 models:
{
     "facebook/bart-large-mnli": {
          "The topic of this article is {}.": {
               "precision": 0.25294098214285715,
               "recall": 0.6,
               "f1": 0.3558618766434079
          },
          "This article is about {}.": {
               "precision": 0.2374696301020407,
               "recall": 0.546,
               "f1": 0.33098517939700417
          },
          "This example is about {}.": {
               "precision": 0.23010520124716557,
               "recall": 0.502,
               "f1": 0.315563421293271
          },
          "This text is about {}.": {
               "precision": 0.2234652892731167,
               "recall": 0.487,
               "f1": 0.3063558417817999
          },
          "The main subject of this text is {}.": {
               "precision": 0.21032846371882102,
               "recall": 0.401,
               "f1": 0.2759292882853235
          },
          "The focus of this writing is on {}.": {
               "precision": 0.15770666666666674,
               "recall": 0.231,
               "f1": 0.18744335059856623
          },
          "The primary topic of discussion in this text is {}.": {
               "precision": 0.12054527777777779,
               "recall": 0.16,
               "f1": 0.137498264787918
          },
          "This article discusses {}.": {
               "precision": 0.051917431468010984,
               "recall": 0.874,
               "f1": 0.09801270299253301
          },
          "The main idea presented in this text is {}.": {
               "precision": 0.13328773545251768,
               "recall": 0.595,
               "f1": 0.2177881041618023
          },
          "The primary subject matter of this article is {}.": {
               "precision": 0.17575694444444448,
               "recall": 0.234,
               "f1": 0.20073912380306755
          },
          "The subject of this article is {}.": {
               "precision": 0.25627924603174596,
               "recall": 0.642,
               "f1": 0.36632545320225784
          },
          "This text covers the topic of {}.": {
               "precision": 0.17151516333856856,
               "recall": 0.784,
               "f1": 0.28145631428308715
          },
          "This article examines {}.": {
               "precision": 0.05235031663665905,
               "recall": 0.824,
               "f1": 0.09844615809385694
          },
          "The main focus of this text is {}.": {
               "precision": 0.14161305555555564,
               "recall": 0.215,
               "f1": 0.17075542507557606
          },
          "This article presents information on {}.": {
               "precision": 0.026869393877447537,
               "recall": 0.941,
               "f1": 0.05224692463388222
          },
          "The main topic covered in this text is {}.": {
               "precision": 0.22207833333333346,
               "recall": 0.343,
               "f1": 0.26960109365368234
          },
          "The central theme of this article is {}.": {
               "precision": 0.1336403475856246,
               "recall": 0.747,
               "f1": 0.22671988609233049
          },
          "This text provides insights into {}.": {
               "precision": 0.02807627583257774,
               "recall": 0.926,
               "f1": 0.05450011090209574
          },
          "This text examines the topic of {} in depth.": {
               "precision": 0.15239098513251717,
               "recall": 0.697,
               "f1": 0.2501004095794428
          },
          "The topic of this text is {}.": {
               "precision": 0.248154574829932,
               "recall": 0.526,
               "f1": 0.3372176839211193
          },
          "This article delves into the topic of {}.": {
               "precision": 0.13962899399098705,
               "recall": 0.893,
               "f1": 0.24149756080747764
          }
     },
     "MoritzLaurer/DeBERTa-v3-base-mnli": {
          "The topic of this article is {}.": {
               "precision": 0.19297588599464013,
               "recall": 0.358,
               "f1": 0.2507745581691509
          },
          "This article is about {}.": {
               "precision": 0.20272309217018195,
               "recall": 0.527,
               "f1": 0.29280989109433425
          },
          "This example is about {}.": {
               "precision": 0.22005519974289137,
               "recall": 0.648,
               "f1": 0.32854078744215565
          },
          "This text is about {}.": {
               "precision": 0.19545455828765018,
               "recall": 0.586,
               "f1": 0.29313635691764084
          },
          "The main subject of this text is {}.": {
               "precision": 0.17078738635192375,
               "recall": 0.319,
               "f1": 0.22246867830572373
          },
          "The focus of this writing is on {}.": {
               "precision": 0.15611546650032596,
               "recall": 0.341,
               "f1": 0.2141770983364737
          },
          "The primary topic of discussion in this text is {}.": {
               "precision": 0.11470831202725923,
               "recall": 0.238,
               "f1": 0.15480541473815768
          },
          "This article discusses {}.": {
               "precision": 0.21711519213886674,
               "recall": 0.713,
               "f1": 0.3328687313213991
          },
          "The main idea presented in this text is {}.": {
               "precision": 0.1638540631423715,
               "recall": 0.363,
               "f1": 0.22578937539524246
          },
          "The primary subject matter of this article is {}.": {
               "precision": 0.1236130281014314,
               "recall": 0.246,
               "f1": 0.1645440100915878
          },
          "The subject of this article is {}.": {
               "precision": 0.20292844660423873,
               "recall": 0.374,
               "f1": 0.2631010465048117
          },
          "This text covers the topic of {}.": {
               "precision": 0.1895825063772857,
               "recall": 0.762,
               "f1": 0.30362447584175134
          },
          "This article examines {}.": {
               "precision": 0.20123091414422556,
               "recall": 0.643,
               "f1": 0.3065310109518975
          },
          "The main focus of this text is {}.": {
               "precision": 0.12584651643396275,
               "recall": 0.255,
               "f1": 0.16852385570513642
          },
          "This article presents information on {}.": {
               "precision": 0.1736452485737942,
               "recall": 0.693,
               "f1": 0.27770568744171187
          },
          "The main topic covered in this text is {}.": {
               "precision": 0.13999918463800334,
               "recall": 0.265,
               "f1": 0.18320917837023026
          },
          "The central theme of this article is {}.": {
               "precision": 0.1416992468146727,
               "recall": 0.279,
               "f1": 0.18794466669777196
          },
          "This text provides insights into {}.": {
               "precision": 0.12879427573665192,
               "recall": 0.613,
               "f1": 0.21286465428211632
          },
          "This text examines the topic of {} in depth.": {
               "precision": 0.07392634195106029,
               "recall": 0.319,
               "f1": 0.12003523594417335
          },
          "The topic of this text is {}.": {
               "precision": 0.2041024260188233,
               "recall": 0.432,
               "f1": 0.2772265736886924
          },
          "This article delves into the topic of {}.": {
               "precision": 0.2270233379089098,
               "recall": 0.676,
               "f1": 0.3398976969560973
          }
     },
     "MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli": {
          "The topic of this article is {}.": {
               "precision": 0.24179061901612467,
               "recall": 0.862,
               "f1": 0.3776504529050626
          },
          "This article is about {}.": {
               "precision": 0.20851196076540474,
               "recall": 0.9,
               "f1": 0.3385813980018553
          },
          "This example is about {}.": {
               "precision": 0.17204123203796348,
               "recall": 0.894,
               "f1": 0.2885533069821489
          },
          "This text is about {}.": {
               "precision": 0.14477989500238422,
               "recall": 0.896,
               "f1": 0.24927996120032483
          },
          "The main subject of this text is {}.": {
               "precision": 0.20279443110122883,
               "recall": 0.872,
               "f1": 0.3290615187484467
          },
          "The focus of this writing is on {}.": {
               "precision": 0.17929048451558446,
               "recall": 0.888,
               "f1": 0.2983441763225319
          },
          "The primary topic of discussion in this text is {}.": {
               "precision": 0.20890603399238533,
               "recall": 0.842,
               "f1": 0.33475662891257696
          },
          "This article discusses {}.": {
               "precision": 0.15616684554262472,
               "recall": 0.914,
               "f1": 0.26675559501861584
          },
          "The main idea presented in this text is {}.": {
               "precision": 0.1350713817818987,
               "recall": 0.88,
               "f1": 0.23419597498535344
          },
          "The primary subject matter of this article is {}.": {
               "precision": 0.20046151511377397,
               "recall": 0.886,
               "f1": 0.32694927509181876
          },
          "The subject of this article is {}.": {
               "precision": 0.23062954176114855,
               "recall": 0.869,
               "f1": 0.36451743824461724
          },
          "This text covers the topic of {}.": {
               "precision": 0.11295899593383177,
               "recall": 0.934,
               "f1": 0.20154314087171135
          },
          "This article examines {}.": {
               "precision": 0.20037822787371734,
               "recall": 0.883,
               "f1": 0.3266338027851091
          },
          "The main focus of this text is {}.": {
               "precision": 0.11389125381064669,
               "recall": 0.875,
               "f1": 0.2015486469322092
          },
          "This article presents information on {}.": {
               "precision": 0.12207980449018145,
               "recall": 0.937,
               "f1": 0.2160154056801496
          },
          "The main topic covered in this text is {}.": {
               "precision": 0.22704627922312143,
               "recall": 0.86,
               "f1": 0.35924836663151194
          },
          "The central theme of this article is {}.": {
               "precision": 0.1704309441678881,
               "recall": 0.898,
               "f1": 0.2864892461196153
          },
          "This text provides insights into {}.": {
               "precision": 0.08882089238631553,
               "recall": 0.956,
               "f1": 0.16254034301971387
          },
          "This text examines the topic of {} in depth.": {
               "precision": 0.2680597846016461,
               "recall": 0.845,
               "f1": 0.40700512429250507
          },
          "The topic of this text is {}.": {
               "precision": 0.18440164481341959,
               "recall": 0.871,
               "f1": 0.3043653256024303
          },
          "This article delves into the topic of {}.": {
               "precision": 0.10805136647897436,
               "recall": 0.947,
               "f1": 0.193970923704079
          }
     }
}