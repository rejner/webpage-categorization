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
