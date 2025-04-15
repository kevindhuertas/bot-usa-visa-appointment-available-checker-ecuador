import React, { FC } from 'react';
import PropTypes from 'prop-types';

interface ILogoProps {
	width?: number;
	height?: number;
}
const Logo: FC<ILogoProps> = ({ width, height }) => {
	return (
		<img src={"/logo.png"} alt="App Logo" style={{ maxWidth: '100%', maxHeight: '40px' }} />
		// <svg
		// 	width={height !== 854 && !!height ? height * (2155 / 854) : width}
		// 	height={width !== 2155 && !!width ? width * (854 / 2155) : height}
		// 	viewBox='0 0 2155 854'
		// 	fill='none'
		// 	xmlns='http://www.w3.org/2000/svg'>
  		// 	<path fill="black" d="m11 9.16318-5-.8017V10.5C6 11.8807 7.11929 13 8.5 13s2.5-1.1193 2.5-2.5V9.16318ZM6.1404 6.35844 11 7.13764V2.08771c-1.14494.19988-2.22828.73028-3.08702 1.47474-.83378.72283-1.49585 1.68517-1.77258 2.79599ZM13 2.08771v4.91232h4.9734c-.1477-1.38214-.8959-2.57887-1.8864-3.43758-.8587-.74446-1.9421-1.27485-3.087-1.47474Zm5 6.91232h-5V11h5V9.00003ZM18 13h-5v2h5v-2Zm0 4h-5v2.5c0 1.3807 1.1193 2.5 2.5 2.5s2.5-1.1193 2.5-2.5V17Z"/>

		// </svg>
	);
};
Logo.propTypes = {
	width: PropTypes.number,
	height: PropTypes.number,
};
Logo.defaultProps = {
	width: 2155,
	height: 854,
};

export default Logo;
