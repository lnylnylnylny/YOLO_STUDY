import { useRef, useState } from "react";

interface ImageItem {
  file: File;
  preview: string;
}

export default function Home() {
  const [image, setImage] = useState<ImageItem | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || !e.target.files[0]) return;
    const file = e.target.files[0];

    if (image) URL.revokeObjectURL(image.preview);

    setImage({ file, preview: URL.createObjectURL(file) });
    e.target.value = "";
  };

  const removeImage = () => {
    if (image) URL.revokeObjectURL(image.preview);
    setImage(null);
  };

  const handleSubmit = () => {
    if (!image) return;
    // 분석 처리 함수 호출
    // processImage(image.file)
    console.log("분석 시작:", image.file.name);
  };

  const tags = [
    "플라스틱",
    "유리병",
    "종이류",
    "캔/금속",
    "음식물",
    "일반쓰레기",
    "비닐",
  ];

  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 bg-white-50">
      {/* 상단 아이콘 */}
      <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mb-4">
        <svg
          className="w-8 h-8"
          viewBox="0 0 24 24"
          fill="none"
          stroke="#3B6D11"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polyline points="1 4 1 10 7 10" />
          <polyline points="23 20 23 14 17 14" />
          <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15" />
        </svg>
      </div>

      <h1 className="text-2xl font-medium text-gray-900 mb-1 text-center">
        재활용 처리 도우미
      </h1>
      <p className="text-sm text-gray-500 mb-8 text-center leading-relaxed">
        사진을 업로드하면 재활용 가능 여부와
        <br />
        올바른 분리수거 방법을 알려드려요
      </p>

      {/* 업로드 영역 */}
      <div
        onClick={() => fileInputRef.current?.click()}
        className={`w-full max-w-sm cursor-pointer rounded-xl overflow-hidden transition
          ${
            image
              ? "border-2 border-solid border-green-600"
              : "border-2 border-dashed border-green-400 bg-green-100 hover:bg-green-200 p-10 flex flex-col items-center gap-2"
          }`}
      >
        {!image ? (
          <>
            <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center mb-1">
              <svg
                className="w-5 h-5"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#3B6D11"
                strokeWidth="1.8"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
            </div>
            <p className="text-sm font-medium text-green-800">
              사진 업로드 또는 촬영
            </p>
            <p className="text-xs text-green-600">JPG, PNG, WEBP 지원</p>
          </>
        ) : (
          <>
            <img
              src={image.preview}
              alt="미리보기"
              className="w-full object-cover block"
            />
            <div
              onClick={(e) => {
                e.stopPropagation();
                fileInputRef.current?.click();
              }}
              className="w-full bg-green-800/80 hover:bg-green-900/90 transition py-2.5 flex items-center justify-center gap-2 text-white text-sm font-medium cursor-pointer"
            >
              <svg
                className="w-3.5 h-3.5"
                viewBox="0 0 24 24"
                fill="none"
                stroke="white"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polyline points="1 4 1 10 7 10" />
                <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10" />
              </svg>
              다른 사진으로 교체
            </div>
          </>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={handleFileChange}
      />

      {/* 파일명 + 삭제 */}
      {image && (
        <div className="w-full max-w-sm mt-2.5 flex items-center gap-2 px-3.5 py-2.5 bg-white border border-gray-200 rounded-lg">
          <svg
            className="w-4 h-4 text-green-600 shrink-0"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
          </svg>
          <span className="text-xs text-gray-500 flex-1 truncate">
            {image.file.name}
          </span>
          <button
            onClick={removeImage}
            className="w-5 h-5 rounded-full border border-gray-300 hover:border-red-300 hover:bg-red-50 flex items-center justify-center text-gray-400 hover:text-red-500 transition text-xs leading-none"
          >
            ✕
          </button>
        </div>
      )}

      {/* 제출 버튼 */}
      <button
        onClick={handleSubmit}
        disabled={!image}
        className="w-full max-w-sm mt-6 py-3.5 rounded-xl font-medium text-sm text-white flex items-center justify-center gap-2 transition active:scale-[0.98]
          bg-green-800 hover:bg-green-900 disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        <svg
          className="w-4 h-4"
          viewBox="0 0 24 24"
          fill="none"
          stroke="white"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
        분리수거 방법 확인하기
      </button>

      {/* 카테고리 태그 */}
      <div className="flex flex-wrap gap-2 justify-center mt-5">
        {tags.map((tag) => (
          <span
            key={tag}
            className="text-xs text-green-800 bg-green-100 border border-green-200 rounded-full px-3 py-1"
          >
            {tag}
          </span>
        ))}
      </div>
    </div>
  );
}
