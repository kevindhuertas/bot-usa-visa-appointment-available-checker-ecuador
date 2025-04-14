import React, { FC, ReactNode, useContext, useEffect, useRef } from 'react';
import ThemeContext from '../../context/themeContext';
import { useFullscreen } from 'react-use';
import useDarkMode from '../../hooks/useDarkMode';
import useMounted from '../../hooks/useMounted';

interface IAppProps {
	children: ReactNode;
}
const App: FC<IAppProps> = ({ children }) => {
	const { mounted } = useMounted();
	useEffect(() => {
		if (mounted) {
			var element = typeof document !== 'undefined' && document.getElementById('__next');
			if (element && 'classList' in element) {
				element?.classList.add('d-flex', 'flex-column', 'flex-grow-1', 'flex-shrink-1');
			}
		}
	}, [mounted]);

	/**
	 * Dark Mode
	 */
	const { darkModeStatus } = useDarkMode();
	useEffect(() => {
		if (darkModeStatus) {
			document.documentElement.setAttribute('theme', 'dark');
		}
		return () => {
			document.documentElement.removeAttribute('theme');
		};
	}, [darkModeStatus]);

	/**
	 * Modern Design
	 */
	useEffect(() => {
		if (process.env.NEXT_PUBLIC_MODERN_DESGIN === 'true') {
			document.body.classList.add('modern-design');
		} else {
			document.body.classList.remove('modern-design');
		}
	});

	/**
	 * Full Screen
	 */
	const { fullScreenStatus, setFullScreenStatus } = useContext(ThemeContext);
	const ref = useRef(null);
	useFullscreen(ref, fullScreenStatus, {
		onClose: () => setFullScreenStatus(false),
	});
	return (
		<div
			ref={ref}
			className='app'
			style={{
				backgroundColor: fullScreenStatus ? 'var(--bs-body-bg)' : undefined,
				zIndex: fullScreenStatus ? 1 : undefined,
				overflow: fullScreenStatus ? 'scroll' : undefined,
			}}>
			{children}
		</div>
	);
};

export default App;
