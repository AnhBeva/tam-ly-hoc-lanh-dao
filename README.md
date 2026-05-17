# Tâm lý học ứng dụng cho quản lý và lãnh đạo

Nền tảng này giúp cấp quản lý, lãnh đạo, trưởng nhóm và người ra quyết định trong tổ chức hiểu tâm lý học ứng dụng từ gốc rễ: khái niệm, bản chất, cơ chế, mô hình, công cụ, ứng dụng, giới hạn và cách thực hành có trách nhiệm trong tổ chức.

## Lời hứa học tập

Sau khi học, người học có thể:

- Nhìn vấn đề con người theo nhiều tầng: cá nhân, quan hệ, nhóm, công việc, hệ thống và văn hóa.
- Phân biệt dữ kiện, diễn giải, giả thuyết và kết luận khi đánh giá hành vi.
- Dùng kiến thức về động lực, cảm xúc, nhận thức, quyền lực, xung đột, an toàn tâm lý và văn hóa để ra quyết định tốt hơn.
- Thiết kế cuộc trò chuyện, phản hồi, ủy quyền, thay đổi và đo lường theo hướng tăng rõ ràng, tự chủ, trách nhiệm và công bằng.
- Nhận ra ranh giới: quản lý không chẩn đoán, không trị liệu, không thao túng và phải chuyển tuyến khi có rủi ro sức khỏe, pháp lý hoặc an toàn.

## Chuẩn giáo trình nâng cấp

Mỗi module được thiết kế như một can thiệp xây năng lực, không chỉ là bài đọc lý thuyết. Cấu trúc học tập đi theo chuỗi:

```text
Vấn đề thật → Bản chất → Nguyên lý → Mô hình tư duy → Quy trình hành động → Case thực chiến → Thực hành có phản hồi → Công cụ mang về → Kết quả đo được
```

Người học không chỉ cần “hiểu khái niệm”, mà phải chứng minh được năng lực qua một tình huống thật: gọi đúng vấn đề, phân biệt triệu chứng và nguyên nhân, chọn tầng can thiệp, nêu rủi ro, đo tín hiệu sau hành động và biết khi nào cần chuyển tuyến.

## Đối tượng và giả định

- Đối tượng: quản lý mới, quản lý cấp trung, trưởng nhóm, founder, HRBP, lãnh đạo chức năng và người chuẩn bị lên vai trò lãnh đạo.
- Độ sâu: giáo trình thực hành chuyên nghiệp, không phải tài liệu self-help ngắn.
- Ngữ cảnh: tổ chức tri thức, vận hành, dịch vụ, sản phẩm, startup hoặc doanh nghiệp đang mở rộng.
- Giới hạn: tài liệu này không thay thế tư vấn tâm lý, tư vấn pháp lý, điều tra nhân sự chính thức hoặc điều trị y tế.

## Cấu trúc tài liệu

- `ban-do-tam-ly-hoc-lanh-dao.md`: bản đồ lĩnh vực và nguyên tắc phân chia.
- `giao-trinh-tam-ly-hoc-lanh-dao.md`: lộ trình học 18 module.
- `thuat-ngu-tam-ly-hoc-lanh-dao.md`: bảng thuật ngữ cốt lõi.
- `cong-cu-thuc-hanh-lanh-dao.md`: bộ công cụ thực hành dùng ngay trong công việc.
- `Module-*.md`: bài học chuyên sâu theo từng chủ đề.
- `assets/module-visuals/module-*.jpg`: ảnh trực quan photorealistic đã tối ưu cho từng module.
- `build_platform_html.py`: script dựng website tĩnh.
- `index.html`: website học tập HTML tĩnh có thể mở trực tiếp trong trình duyệt.

## Nguồn tham chiếu nền

Nội dung được tổng hợp theo các nguyên lý ổn định của tâm lý học ứng dụng, tâm lý học tổ chức, khoa học hành vi và quản trị. Một số nguồn chính thức được dùng để đặt ranh giới và kiểm tra điểm nhạy cảm:

- WHO, `Guidelines on mental health at work`: https://www.who.int/publications/i/item/9789240053052
- WHO, `Mental health at work` cập nhật ngày 2/9/2024: https://www.who.int/news-room/fact-sheets/detail/mental-health-at-work
- ISO 45003:2021, `Psychological health and safety at work`: https://www.iso.org/standard/64283.html
- National Academies, `Enhancing the Effectiveness of Team Science`: https://www.nationalacademies.org/publications/19007
- APA, các chủ đề phổ thông về khoa học tâm lý và nơi làm việc: https://www.apa.org/topics

## Cách build website

```bash
python3 build_platform_html.py
```

Sau khi build, mở `index.html` trong trình duyệt. Website là HTML tĩnh, không cần backend.

## Website HTML tĩnh

Khi chỉnh sửa nội dung, hãy cập nhật các file Markdown nguồn trước, sau đó chạy lại:

```bash
python3 build_platform_html.py
```

Website được build vào `index.html`, dùng logo Lumi từ `assets/lumi-logo-2022.png` và ảnh trực quan từng chương trong `assets/module-visuals/`. Không cần backend hoặc build tool phía client.

## Nguyên tắc sử dụng có trách nhiệm

- Không dùng thuật ngữ tâm lý để gắn nhãn, làm xấu hổ hoặc kết luận bản chất con người.
- Không dùng kỹ thuật ảnh hưởng để che giấu mục tiêu, ép phục tùng hoặc khai thác điểm yếu.
- Luôn phân biệt quan sát, diễn giải, giả thuyết và kết luận.
- Khi có dấu hiệu rủi ro sức khỏe tâm thần, quấy rối, bạo lực, tự hại, phân biệt đối xử, vi phạm pháp lý hoặc an toàn, hãy dùng kênh chuyên môn phù hợp.
