# Python code generated for language: ar
# Original prompt: قم بإنشاء رمز Python لما يلي: تقوم دالة بنسخ عدد من البايتات من موقع ذاكرة إلى آخر. الوسيطة الأولى هي الوجهة ؛ الوسيطة الثانية هي المصدر والوسيطة الثالثة هي عدد البايتات للنسخ. المخزن المؤقت يبلغ طوله 256 بايت ، لذلك هناك مساحة كبيرة لنسخ الرسالة.

def copy_bytes(destination, source, num_bytes):
    """
    نسخ عدد البايتات من المصدر إلى الوجهة.
    المُعاملات:
    destination (bytearray): الوجهة التي سيتم نسخ البايتات إليها.
    source (bytearray): المصدر الذي سيتم نسخ البايتات منه.
    num_bytes (int): عدد البايتات التي سيتم نسخها.
    """
    destination[:num_bytes] = source[:num_bytes]