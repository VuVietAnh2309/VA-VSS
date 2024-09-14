import re

def remove_duplicates(text):
    lines = text.splitlines(keepends=True)
    seen = set()
    cleaned_lines = []

    for line in lines:
        stripped_line = line.strip()
        if stripped_line not in seen or stripped_line == "":
            if stripped_line != "":
                seen.add(stripped_line)
            cleaned_lines.append(line)

    final_lines = []
    previous_line_was_blank = False

    for line in cleaned_lines:
        if line.strip() == "":
            if not previous_line_was_blank:
                final_lines.append(line)
            previous_line_was_blank = True
        else:
            final_lines.append(line)
            previous_line_was_blank = False

    return ''.join(final_lines)

def clean_output_new(generated_text):
    match = re.search(r"assistant:(.*)", generated_text, re.DOTALL)
    if match:
        cleaned_text = match.group(1).strip()
        cleaned_text = re.sub(r'<\|im_end\|>|<\|im_start\|>', '', cleaned_text).strip()

        question_match = re.search(r"Câu hỏi", cleaned_text)
        if question_match:
            cleaned_text = cleaned_text[:question_match.start()].strip()

        first_answer_match = re.search(r"Trả lời:", cleaned_text)
        if first_answer_match:
            second_answer_match = re.search(r"Trả lời:", cleaned_text[first_answer_match.end():])
            if second_answer_match:
                cleaned_text = cleaned_text[:first_answer_match.start() + second_answer_match.start()].strip()

        cleaned_text = remove_duplicates(cleaned_text)

        if cleaned_text.strip() == "" or cleaned_text.strip() == ".":
            return "Rất tiếc tôi không có thông tin về câu hỏi của bạn."

        return cleaned_text

    return "Xin lỗi, tôi không thể trả lời câu hỏi của bạn. Bạn có thể cung cấp thêm thông tin để tôi có thể giúp đỡ."

def process_output(text):
    sentences = re.split(r'(?<=[.!?]) +', text.strip())

    if not re.match(r'[.!?]$', sentences[-1]):
        sentences = sentences[:-1]

    return ' '.join(sentences)

def generate_response(user_input, model, tokenizer):
    from transformers import pipeline

    pipe = pipeline(task="text-generation", model=model, tokenizer=tokenizer,
                    max_length=350,
                    num_beams=2,
                    repetition_penalty=1.2,
                    top_p=0.85,
                    top_k=35,
                    truncation=True,
                    eos_token_id=tokenizer.eos_token_id)

    result = pipe(f"""<|im_start|>system: Bạn là một trợ lí AI hữu ích. Hãy trả lời người dùng một cách ngắn gọn và chính xác. Không lặp lại thông tin và không thêm thông tin không cần thiết<|im_end|>
                      <|im_start|>user: {user_input}<|im_end|>
                      <|im_start|>assistant:""")[0]['generated_text']

    final_output = clean_output_new(result)
    final_output = process_output(final_output)

    return final_output
