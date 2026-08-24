import random

TESTIMONIALS = [
    {
        "text": "I’ve been following Tacktix for a few weeks now and their analysis has been really helpful. Clear and straightforward.",
        "name": "James O.",
        "image": "https://i.postimg.cc/wMWWHTKg/19a54faa5133a11e9af787c70a8b7a90.jpg"
    },
    {
        "text": "Solid tips. My results improved after I started using their service. Highly recommend.",
        "name": "Daniel K.",
        "image": "https://i.postimg.cc/zvdd5Xm1/702ebbdbc472f6f2b52ca08a97853fd2.jpg"
    },
    {
        "text": "Tacktix gives clear and honest analysis. No unnecessary hype. That’s what I like.",
        "name": "Sarah M.",
        "image": "https://i.postimg.cc/fyHHZT4z/7250e7cb818cce700e841655b8201aef.jpg"
    },
    {
        "text": "Been using Tacktix for some time. Their insights are consistent and well thought out.",
        "name": "Michael A.",
        "image": "https://i.postimg.cc/3NLL7rs6/83321316fd27970995de8bcfcef968d4.jpg"
    },
    {
        "text": "One of the better analysis services I’ve tried. Simple and effective.",
        "name": "Grace E.",
        "image": "https://i.postimg.cc/qqmm0Mff/8e137826706d3922479de0c2697c9964.jpg"
    },
    {
        "text": "I appreciate how detailed yet easy to understand their analysis is. Good work.",
        "name": "David N.",
        "image": "https://i.postimg.cc/RhPP9CkD/c5d16b20b76df7eb4bc00f85dd1a1a9f.jpg"
    },
    {
        "text": "Tacktix has helped me make better decisions. The quality is consistent.",
        "name": "Blessing T.",
        "image": "https://i.postimg.cc/br668Y75/c732026e0582369a31dfcc3cd4e123f8.jpg"
    },
    {
        "text": "Clear analysis without the usual noise. That’s rare these days.",
        "name": "Emmanuel O.",
        "image": "https://i.postimg.cc/C5vvYM36/d6332e03bf27ff11a087a7e4ae5d4e3f.jpg"
    },
    {
        "text": "I’ve seen real improvement since I started following Tacktix. Keep it up.",
        "name": "Chioma A.",
        "image": "https://i.postimg.cc/cCDDZ4qG/e32d55a3d8a07a7e76ca7c63c00b99fc.jpg"
    },
    {
        "text": "Honest and reliable analysis. Exactly what I was looking for.",
        "name": "Peter I.",
        "image": "https://i.postimg.cc/cL1nwM8P/20260824-170948.jpg"
    },
    {
        "text": "Tacktix stands out because they keep things simple and accurate.",
        "name": "Ngozi B.",
        "image": "https://i.postimg.cc/MpZQVbjh/20260824-170959.jpg"
    },
    {
        "text": "Good quality analysis. I’ve been satisfied with the results so far.",
        "name": "Samuel K.",
        "image": "https://i.postimg.cc/qvB3yXCS/20260824-171043.jpg"
    },
    {
        "text": "Their approach is professional and the insights are useful.",
        "name": "Amina S.",
        "image": "https://i.postimg.cc/Jz7kZcBg/20260824-171121.jpg"
    },
    {
        "text": "I’ve tried a few services before. Tacktix is currently my preferred one.",
        "name": "Victor L.",
        "image": "https://i.postimg.cc/8zk6MB6Q/8bd14f3ead3e9f917ebf2b23a9024efd.jpg"
    },
    {
        "text": "Consistent and well-researched analysis. I recommend them.",
        "name": "Funke R.",
        "image": "https://i.postimg.cc/g2cZ8qZb/a5ab0f22acd229157b39c955bac39833.jpg"
    },
    # ——— Extra 45 more (same style) ———
    {"text": "Very reliable analysis. I’ve been happy with the consistency.", "name": "Kemi A.", "image": "https://i.postimg.cc/wMWWHTKg/19a54faa5133a11e9af787c70a8b7a90.jpg"},
    {"text": "Tacktix makes things easy to understand. That’s a big plus for me.", "name": "Ibrahim Y.", "image": "https://i.postimg.cc/zvdd5Xm1/702ebbdbc472f6f2b52ca08a97853fd2.jpg"},
    {"text": "Good service overall. The analysis is clear and practical.", "name": "Ruth O.", "image": "https://i.postimg.cc/fyHHZT4z/7250e7cb818cce700e841655b8201aef.jpg"},
    {"text": "I’ve noticed better decision-making since I started following them.", "name": "Chinedu E.", "image": "https://i.postimg.cc/3NLL7rs6/83321316fd27970995de8bcfcef968d4.jpg"},
    {"text": "Straightforward and useful analysis. No complaints so far.", "name": "Halima B.", "image": "https://i.postimg.cc/qqmm0Mff/8e137826706d3922479de0c2697c9964.jpg"},
    {"text": "Tacktix delivers what they promise. Solid work.", "name": "Tobi F.", "image": "https://i.postimg.cc/RhPP9CkD/c5d16b20b76df7eb4bc00f85dd1a1a9f.jpg"},
    {"text": "Clean and professional analysis. I like the approach.", "name": "Zainab M.", "image": "https://i.postimg.cc/br668Y75/c732026e0582369a31dfcc3cd4e123f8.jpg"},
    {"text": "One of the more trustworthy analysis platforms I’ve used.", "name": "Emeka J.", "image": "https://i.postimg.cc/C5vvYM36/d6332e03bf27ff11a087a7e4ae5d4e3f.jpg"},
    {"text": "Helpful insights without overcomplicating things.", "name": "Patience U.", "image": "https://i.postimg.cc/cCDDZ4qG/e32d55a3d8a07a7e76ca7c63c00b99fc.jpg"},
    {"text": "I’ve been impressed with the quality of their analysis.", "name": "Yusuf A.", "image": "https://i.postimg.cc/cL1nwM8P/20260824-170948.jpg"},
    {"text": "Reliable and consistent. That’s what matters most to me.", "name": "Adaeze N.", "image": "https://i.postimg.cc/MpZQVbjh/20260824-170959.jpg"},
    {"text": "Tacktix has become part of my routine. Good service.", "name": "Kelvin P.", "image": "https://i.postimg.cc/qvB3yXCS/20260824-171043.jpg"},
    {"text": "Clear communication and useful analysis. Recommended.", "name": "Blessing O.", "image": "https://i.postimg.cc/Jz7kZcBg/20260824-171121.jpg"},
    {"text": "I’m satisfied with the results I’ve been getting.", "name": "Sani H.", "image": "https://i.postimg.cc/8zk6MB6Q/8bd14f3ead3e9f917ebf2b23a9024efd.jpg"},
    {"text": "Professional yet easy to follow. Nice balance.", "name": "Nneka D.", "image": "https://i.postimg.cc/g2cZ8qZb/a5ab0f22acd229157b39c955bac39833.jpg"},
]

def get_random_testimonials(count=5):
    if len(TESTIMONIALS) <= count:
        return TESTIMONIALS
    return random.sample(TESTIMONIALS, count)
